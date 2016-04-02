from hexformat import SRecord


def test_readsrec():
    from hexformat import SRecord
    srec = SRecord.fromfile("random1.s19")
    execute_startaddress = srec.startaddress
    header_line = srec.header
    first_address = srec.start()
    last_address = srec.end()
