"""
Utility functions
"""

def time_str(tsec, withdays=False):
    """
    convert time in seconds to a string in HH:MM:SS format, with optional days
    """

    days, remainder = divmod(tsec, 24*3600)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    if withdays:
        t_str = '%i days, %i:%s:%s' \
                       % (days,hours,\
                          str(int(minutes)).zfill(2),\
                          str(int(seconds)).zfill(2))
    else:
        hours = hours + 24*days
        t_str = '%i:%s:%s' \
                       % (hours,\
                          str(int(minutes)).zfill(2),\
                          str(int(seconds)).zfill(2))
    return t_str
    

