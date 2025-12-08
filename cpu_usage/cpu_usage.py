# -*- coding: utf-8 -*-
"""
Created on Thu May 19 11:52:25 2022

@author: Simon
"""
import time
import logging
from threading import Thread
from multiprocessing import Process, Manager
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
from joblib import Parallel, delayed
import matplotlib.dates as mdates
import datetime as dt

class ProcessEnumerator(Process):
    
    def __init__(self, pattern, pids):
        self.pattern = pattern
        self.pids = pids
        super(ProcessEnumerator, self).__init__()
        initial_pids = []
        for proc in psutil.process_iter():
            if self.pattern.lower() in proc.name().lower() and \
                proc.status()=='running':
                initial_pids += [proc.pid]
        self.pids.append(initial_pids)
                
    def run(self):
        self.running = True

        while self.running:
            pids = []
            for proc in psutil.process_iter():

                try:
                    if self.pattern in proc.name() and proc.status()=='running':
                        pids += [proc.pid]
                except psutil.NoSuchProcess:
                    pass
            try:
                self.pids.append(pids)
            except (BrokenPipeError, EOFError):
                return
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                self.kill()
                self.join()
                return

    def stop(self):
        self.running = False

    def __delete__(self):
        self.running = False


class CPUUsageLogger():
    """
    A class that monitors the CPU usage of all processes or
    threads with a certain name e.g 'python.exe' 
    """
    
    def __init__(self, process_name='python', interval=500):
        self.manager = Manager()
        logging.info('getting initial process list')
        self.segname = 'init'
        self.name = process_name
        self.data = []
        self.running = False
        self.interval = interval     
        self.pids = self.manager.list()
        self.proc_enum = ProcessEnumerator(process_name, self.pids)
        self.proc_enum.start()
        self.processes = {}
        self.update_processes()
                
    
    def set_segment_name(self, name):
        # make copy so that segment is not ending too early
        self.data += [(time.time(), self.data[-1][1], self.segname, len(self.processes))]   

        self.segname = name
        
    def start(self, name='init'):
        if self.running: 
            self.set_segment_name(name)
            # logging.warning('already running')
            return
        self.segname=name
        self.running = True
        self.thread_loop = Thread(target=self._loop)
        self.thread_loop.start()

    def stop(self):
        self.running = False
        self.manager.shutdown()
        self.thread_loop.join()
        self.proc_enum.stop()
        self.proc_enum.kill()
       
    def update_processes(self):
        try:
            pids = self.pids[-1]
        except BrokenPipeError:
            return
                
        for pid in pids:
            if not (pid in self.processes):
                try:
                    self.processes[pid] = psutil.Process(pid)
                    # call once, else the first call will be 0.0%
                    self.processes[pid].cpu_percent()
                except psutil.NoSuchProcess:
                    pass
                
        for proc in list(self.processes.values()):
            try:
                if proc.status()!='running' or proc.pid not in pids:
                    try:
                        del self.processes[proc.pid]
                    except KeyError:
                        pass
            except psutil.NoSuchProcess:
                try:
                    del self.processes[proc.pid]
                except KeyError:
                    pass
                
        time.sleep(0.1)
                

    def _loop(self):
        cpu_count = psutil.cpu_count()
        while self.running:
            self.update_processes()
            percs = []
            for proc in self.processes.values():
                try:
                    percs += [proc.cpu_percent()/cpu_count]
                except psutil.NoSuchProcess:
                    pass
            perc_sum = sum(percs)
            self.data += [(time.time(), perc_sum, self.segname, len(self.processes))]   
            time.sleep(self.interval/1000)
            
            
    def plot(self, block=False):
        if self.running:
            self.stop()
        if len(self.data)==0:
            logging.error('Nothing to plot. Maybe logging did not work or process "{self.name}" was not found?')
            return
        # print(self.data)
        times = [dt.datetime.fromtimestamp(x[0]) for x in self.data]       
        percs = [x[1] for x in self.data]       
        segs  = [x[2] for x in self.data]       
        nproc = [x[3] for x in self.data]   
        
        plt.figure()
        ax = plt.gca()
        line1 = plt.plot(times, percs, label='CPU utilization')
        ax.set_ylim(0, 107)
        ax.set_title(f'CPU utilization for "{self.name}"')
        max_thread_cpu = 100/psutil.cpu_count()
        ax.hlines([i*max_thread_cpu for i in range(int(100/max_thread_cpu)+1)], times[0],  times[-1], 
                   colors='gray', linestyle='dashed', alpha=0.4, linewidth=1)
        
        curr_seg = segs[0]
        curr_seg_start = 0
        colors = enumerate(sns.color_palette('pastel',
                                             n_colors=len(set(segs)),
                                             as_cmap=True))
        
        for i, seg in enumerate(segs):
            if seg!=curr_seg:
                # center = times[int(round((curr_seg_start+i)/2))]
                ax.text(times[curr_seg_start+1], 50, curr_seg, fontsize=15, alpha=0.5,
                        horizontalalignment='left', rotation=90,
                        verticalalignment='center')
                ax.axvspan(times[curr_seg_start], times[i], 
                            color=next(colors)[1], 
                            alpha=0.3)
                curr_seg = seg
                curr_seg_start = i
                
        # center = times[int(round((curr_seg_start+i)/2))]
        ax.text(times[curr_seg_start+1], 50, seg, fontsize=15, alpha=0.5,
                horizontalalignment='left', rotation=90,
                verticalalignment='center')
        ax.axvspan(times[curr_seg_start], times[-1], color=next(colors)[1], alpha=0.3)
        myFmt = mdates.DateFormatter('%H:%M:%S')
        ax.xaxis.set_major_formatter(myFmt)
                
        line2 = ax.plot(times, nproc, alpha=1, color='green', linestyle='dotted')
        ax.set_ylabel(f'CPU Percentage used by processes "{self.name}"')
        
        ax.legend(line1+ line2, ['CPU utilization', '# processes'], loc='lower right')
        plt.show(block=block)
                

def dummy_calculation(timeout=5):
    start = time.time()
    while time.time()-start<timeout:
        20**20
       
if __name__=='__main__':
    cpu_count = psutil.cpu_count()

    self = CPUUsageLogger()
    self.start('single core')
    
    print('single core')
    dummy_calculation()
    
    self.set_segment_name('quarter load')
    print('multi core (quarter load)')
    Parallel(n_jobs=cpu_count//4)(delayed(dummy_calculation)() for i in range(cpu_count//4))
            
    self.set_segment_name('half load')
    print('multi core (half load)')
    Parallel(n_jobs=-1)(delayed(dummy_calculation)() for i in range(cpu_count//2))

    self.set_segment_name('full load')
    print('multi core (full load)')
    Parallel(n_jobs=-1)(delayed(dummy_calculation)() for i in range(cpu_count))

    print('stop')
    self.stop()
    self.plot()
    plt.show(block=True)