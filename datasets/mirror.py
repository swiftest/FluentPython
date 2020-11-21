import contextlib


class LookingGlass:
    
    def __enter__(self):
        # 当with语句开始执行时，解释器会在上下文管理器对象上调用__enter__方法
        import sys
        self.original_write = sys.stdout.write
        sys.stdout.write = self.reverse_write
        return 'JABBERWOCKY'
    
    def reverse_write(self, text):
        self.original_write(text[::-1])
        
    def __exit__(self, exc_type, exc_value, traceback):    
        # 当with语句运行结束后，解释器通常需要调用sys.exc_info()，得到的就是__exit__接收的这三个参数，用来判断做什么清理工作。
        import sys
        sys.stdout.write = self.original_write
        if exc_type is ZeroDivisionError:
            print('Please DO NOT divide by zero!')
            return True
    

@contextlib.contextmanager
def looking_glass():
    import sys
    original_write = sys.stdout.write
    
    def reverse_write(text):
        original_write(text[::-1])
        
    sys.stdout.write = reverse_write
    msg = ''
    try:
        yield 'JABBERWOCKY'
    except ZeroDivisionError:
        msg = 'Please DO NOT divide by zero!'
        # raise ZeroDivisionError
    finally:
        sys.stdout.write = original_write
        if msg:
            print(msg)
