#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步处理助手 - 提升响应速度和用户体验
自动生成，用于第三阶段D性能优化
"""

import threading
import queue
import time
from typing import Callable, Any, Optional
from PyQt5.QtCore import QThread, pyqtSignal, QObject

class AsyncTaskWorker(QThread):
    """异步任务工作线程"""
    
    task_completed = pyqtSignal(object)  # 任务完成信号
    task_failed = pyqtSignal(str)        # 任务失败信号
    
    def __init__(self, task_func: Callable, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.error = None
    
    def run(self):
        """执行任务"""
        try:
            self.result = self.task_func(*self.args, **self.kwargs)
            self.task_completed.emit(self.result)
        except Exception as e:
            self.error = str(e)
            self.task_failed.emit(self.error)

class BackgroundTaskManager(QObject):
    """后台任务管理器"""
    
    def __init__(self):
        super().__init__()
        self.active_tasks = []
    
    def run_async_task(self, task_func: Callable, success_callback: Optional[Callable] = None, 
                      error_callback: Optional[Callable] = None, *args, **kwargs):
        """运行异步任务"""
        worker = AsyncTaskWorker(task_func, *args, **kwargs)
        
        if success_callback:
            worker.task_completed.connect(success_callback)
        
        if error_callback:
            worker.task_failed.connect(error_callback)
        
        # 任务完成后清理
        worker.finished.connect(lambda: self._cleanup_task(worker))
        
        self.active_tasks.append(worker)
        worker.start()
        
        return worker
    
    def _cleanup_task(self, worker):
        """清理完成的任务"""
        if worker in self.active_tasks:
            self.active_tasks.remove(worker)
    
    def cancel_all_tasks(self):
        """取消所有任务"""
        for worker in self.active_tasks:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        self.active_tasks.clear()

class ThreadPoolManager:
    """线程池管理器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.task_queue = queue.Queue()
        self.workers = []
        self.running = False
    
    def start(self):
        """启动线程池"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """停止线程池"""
        self.running = False
        # 添加停止信号到队列
        for _ in range(self.max_workers):
            self.task_queue.put(None)
    
    def submit_task(self, task_func: Callable, callback: Optional[Callable] = None, *args, **kwargs):
        """提交任务"""
        task = {
            'func': task_func,
            'args': args,
            'kwargs': kwargs,
            'callback': callback
        }
        self.task_queue.put(task)
    
    def _worker_loop(self):
        """工作线程循环"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:  # 停止信号
                    break
                
                # 执行任务
                try:
                    result = task['func'](*task['args'], **task['kwargs'])
                    if task['callback']:
                        task['callback'](result)
                except Exception as e:
                    print(f"任务执行失败: {e}")
                
                self.task_queue.task_done()
                
            except queue.Empty:
                continue

# 全局实例
background_task_manager = BackgroundTaskManager()
thread_pool_manager = ThreadPoolManager()

def get_background_task_manager() -> BackgroundTaskManager:
    """获取后台任务管理器"""
    return background_task_manager

def get_thread_pool_manager() -> ThreadPoolManager:
    """获取线程池管理器"""
    return thread_pool_manager

def run_in_background(task_func: Callable, success_callback: Optional[Callable] = None,
                     error_callback: Optional[Callable] = None, *args, **kwargs):
    """在后台运行任务"""
    return background_task_manager.run_async_task(
        task_func, success_callback, error_callback, *args, **kwargs
    )

def submit_to_thread_pool(task_func: Callable, callback: Optional[Callable] = None, *args, **kwargs):
    """提交任务到线程池"""
    thread_pool_manager.submit_task(task_func, callback, *args, **kwargs)
