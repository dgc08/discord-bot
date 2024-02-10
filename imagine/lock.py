import os
import msvcrt

class FileAlreadyLockedException(Exception):
    def __init__(self, file, message=None):
        if message is None:
            message = f"The file {file} is already locked."
        super().__init__(message)

class Lock:
    def __init__(self, file_location: str):
        self._loc = file_location

    def lock(self):
        try:
            self._lock = open(self._loc, 'wb')
            msvcrt.locking(self._lock.fileno(), msvcrt.LK_NBLCK, 1)
        except IOError:
            # File already exists
            raise FileAlreadyLockedException(self._loc)

    def unlock(self):
        if self._lock:
            msvcrt.locking(self._lock.fileno(), msvcrt.LK_UNLCK, 1)
            self._lock.close()
            os.remove(self._loc)
def test():
    lo = Lock("test.lock")
    try:
        lo.lock()
        input("Lock acquired. Press Enter to unlock.")
    except FileAlreadyLockedException as e:
        print(e)

if __name__ == "__main__":
    test()


