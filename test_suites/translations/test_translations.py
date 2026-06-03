import time


def test_keyfob(can_bus):


    can_bus.send_periodic_signal('CmdIgnStat', 0x4)
    time.sleep(1)
    #Setting Language
#     can_bus.send_signal('CFG_RQ', 'CFG_FEATURE', 0xA)
#     time.sleep(1)
#     can_bus.send_signal('CFG_RQ', 'CFG_STAT_RQ', 0x3)
#     time.sleep(1)

    
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0x0)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

       
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0x2)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

       
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0x3)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

      
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0x4)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

      
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0x5)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

      
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0x6)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

#        #German
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0x7)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

#        #German
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0x9)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

#        #German
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0xA)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

#        #German
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0xB)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

#        #German
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0xC)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

#        #German
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0xD)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

#        #German
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0x10)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

#        #German
#     can_bus.send_signal('CFG_RQ', 'CFG_SET', 0x11)
#     time.sleep(2)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x1)
#     time.sleep(3)
#     can_bus.send_periodic_signal('MsgFobBattLow', 0x0)
#     time.sleep(3)

#     assert True


# def test_EPStoohot(can_bus):


#     can_bus.send_periodic_signal('CmdIgnStat', 0x4)
#     time.sleep(10)

    
#     can_bus.send_periodic_signal('EPS_Warn_Disp_Rq', 0x1)
#     time.sleep(6)
    
#     can_bus.send_periodic_signal('EPS_Warn_Disp_Rq', 0x2)
#     time.sleep(6)

    assert True

if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])