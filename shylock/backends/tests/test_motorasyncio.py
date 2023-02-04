from pymongo.errors import WriteError

from shylock.backends.motorasyncio import ShylockMotorAsyncIOBackend


def test_check_retry_exception():
    msg = "Error=16500, RetryAfterMs=125, Details="
    details = {"errmsg": msg}
    e = WriteError(msg, code=16500, details=details)
    delay = ShylockMotorAsyncIOBackend._check_retry_exception(e)
    assert delay == 0.125
