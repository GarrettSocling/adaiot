from Adafruit_IO import Client
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

import threading

class ChartThread(threading.Thread):
    def __init__(self, client_key, feed_name, out_dir):
        threading.Thread.__init__(self)
        self._client_key = client_key
        self._feed_name = feed_name
        self._out_dir = out_dir

    def run(self):
        print "ChartThread connecting"
        aio = Client(self._client_key)
    
        print "ChartThread fetching data"
        data = aio.data(self._feed_name)
    
        today = datetime.datetime.now()
        one_day = datetime.timedelta(days=1)
        yesterday = today - one_day
    
        dates = []
        temps = []
    
        print "ChartThread treating data"
        for d in data:
            ts = datetime.datetime.fromtimestamp(d.created_epoch)
            if ts > yesterday:
                dates.append(ts)
                temps.append(d.value)
    
        print "ChartThread plotting"
        dates = date2num(dates)
    
        fig = plt.figure()
        fig.set_size_inches(4, 3)
        plt.subplots_adjust(left=0.0, right=0.925, bottom=0.0, top=0.948)
        ax = fig.add_subplot(111)
        ax.plot_date(dates, temps, '-')
        ax.axes.get_xaxis().set_visible(False)
        plt.savefig(self._out_dir+'temps.png', dpi = 80, bbox_inches='tight', pad_inches = 0)
        plt.close(fig)
        print "ChartThread done"
