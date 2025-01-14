#  Python Module for import                           Date : 2015-02-21
#  vim: set fileencoding=utf-8 ff=unix tw=78 ai syn=python : per Python PEP 0263 
''' 
_______________|  yi_timeseries : essential time series functions.

REFERENCES:

- Holt-Winters two-parameter linear growth exponential smoothing model:

  - Spyros Makridakis, 1978, _FORECASTING_, pp. 64-66.
       H-W does extremely well against ARIMA models.
  - Rob Hyndman, 2008, _Forecasting with Exponential Smoothing_,
       discusses level, growth (linear), and seasonal variants.
  - Sarah Gelper, 2007, _Robust Forecasting with Exponential 
       and Holt-Winters smoothing_, useful for parameter values.

- Computational tools for pandas
  http://pandas.pydata.org/pandas-docs/stable/computation.html

N.B. -  rolling_* methods, including rolling_apply, only work on one-dimensional 
array, thus we may work outside pandas in numpy, then bring back the results.
See holt_winters_growth() vs. holt().


CHANGE LOG  For latest version, see https://github.com/rsvp/fecon235
2015-02-21  Add holtgrow and holtpc functions.
               Fix holtlevel to truly include alpha and beta.
2014-09-21  Improve holt() by eliminating paste operation, 
               and using todf from yi_1tools.
2014-09-15  Change HW alpha and beta defaults based on Gelper 2007.
2014-08-09  Clean-up graveyard and comments.
2014-08-08  First version covers Holt-Winters linear model.
'''

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from yi_1tools import todf

#  Holt-Winters default parameters
hw_alpha = 0.26      #  Based on robust optimization in Gelper 2007,
hw_beta  = 0.19      #  for Gaussian, fat tail, and outlier data.



def holt_winters_growth( y, alpha=hw_alpha, beta=hw_beta ):
     '''Helper for Holt-Winters growth (linear) model using numpy arrays.'''
     #  N.B. -  SEASONAL variant of Holt-Winters is omitted.
     N = y.size             #  y should be a numpy array.
     #                         0 < alpha and beta < 1
     alphac = 1 - alpha     #  Complements of alpha and beta
     betac  = 1 - beta      #     pre-computed before the loop.
     #   Create ndarrays filled with zeros to be updated 
     #   as the y data comes in:
     l = np.zeros(( N, ))   #  Fill level array with zeros.
     l[0] = y[0]            #  Initialize level.
     b = np.zeros(( N, ))   #  Smoothed one-step growths.
     b[0] = y[1] - y[0]     #  Let's guess better than dummy b[0]=0.
     for i in range( 1, N ):
          l[i] = (alpha * y[i]) + (alphac * (l[i-1] + b[i-1]))
          ldelta = l[i] - l[i-1]
          #      ^change in smoothed data = proxy for implicit growth.
          b[i] = (beta * ldelta) + (betac * b[i-1])
          #              ^not ydelta !!
     return [ l, b ]
     #        ^^^^ these are arrays.




def holt( data, alpha=hw_alpha, beta=hw_beta ):
     '''Holt-Winters growth (linear) model outputs workout dataframe.'''
     #  holt is an EXPENSIVE function, so retain its output for later.
     holtdf = todf( data ).dropna()
     #              'Y'    ^else: 
     #     "ValueError: Length of values does not match length of index"
     y = holtdf.values      #  Convert to array.
     l, b = holt_winters_growth( y, alpha, beta )
     holtdf['Level']  = l
     holtdf['Growth'] = b
     #    In effect, additional columns 'Level' and 'Growth'
     #    for smoothed data and local slope, 
     #    along side the original index and given data:
     return holtdf


def holtlevel( data, alpha=hw_alpha, beta=hw_beta ):
     '''Just smoothed Level dataframe from Holt-Winters growth model.'''
     #  Useful to filter out seasonals, e.g. see X-11 method:
     #     http://www.sa-elearning.eu/basic-algorithm-x-11
     return todf( holt( data, alpha, beta )['Level'] )


def holtgrow( data, alpha=hw_alpha, beta=hw_beta ):
     '''Just the Growth dataframe from Holt-Winters growth model.'''
     #  In terms of units expressed in data.
     return todf( holt( data, alpha, beta )['Growth'] )


def holtpc( data, yearly=256, alpha=hw_alpha, beta=hw_beta ):
     '''Annualized percentage growth dataframe from H-W growth model.'''
     #  yearly is the multiplier to annualize Growth.
     #
     #       MOST VALUABLE H-W function              <= !!
     #       It contains the HISTORY of FORECASTED RATES!
     #
     holtdf = holt( data, alpha, beta )
     level  = todf( holtdf['Level'] )
     grow   = todf( holtdf['Growth'] )
     growan = todf( grow * yearly )
     return todf( 100 * ( growan / level ) )


def holtforecast( holtdf, h=12 ):
     '''Given a dataframe from holt, forecast ahead h periods.'''
     #  N.B. -  holt forecasts by multiplying latest growth 
     #          by the number of periods ahead. Somewhat naive...
     #          notice that the growth is based on smoothed levels.
     last = holtdf[-1:]
     y, l, b = last.values.tolist()[0]
     #         df to array to list, but extract first element :-(
     forecasts = [y] + [ l + (b*(i+1)) for i in range(h) ]
     #            ^last actual point
     return todf( forecasts, 'Forecast' )


def plotholt( holtdf, h=12 ):
     '''Given a dataframe from holt, plot forecasts h periods ahead.'''
     #  plotdf will not work since index there is assumed to be dates.
     holtforecast( holtdf, h ).plot( title='Holt-Winters linear forecast')
     return



# ====================================== GRAVEYARD =============================

#  #  Table 3-8 from Makridakis 1978:
#  makridakis_p65 = np.array( [ 143, 152, 161, 139, 137, 174, 142, 141, 162, 
#                     180, 164, 171, 206, 193, 207, 218, 229, 225, 204, 227, 
#                     223, 242, 239, 266 ] )


if __name__ == "__main__":
     print "\n ::  THIS IS A MODULE for import -- not for direct execution! \n"
     raw_input('Enter something to get out: ')
