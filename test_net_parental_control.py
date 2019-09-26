from net_parental_control import *

def test_parse_rule_entry():
    entry = Entry()
    entry = parse_rule_entry_line('InternetGatewayDevice.TimeRestriction.RestRules.1.InternetAllowed=0', entry)
    assert(entry.internet_allowed == 0)
    entry = parse_rule_entry_line('InternetGatewayDevice.TimeRestriction.RestRules.1.Username=User', entry)
    assert(entry.username == "User")
    entry = parse_rule_entry_line('InternetGatewayDevice.TimeRestriction.RestRules.1.MACAddr=88:88:88:88:88:88', entry)
    assert(entry.mac_address == "88:88:88:88:88:88")
    entry = parse_rule_entry_line('InternetGatewayDevice.TimeRestriction.RestRules.1.WeekDays=Sun,Mon,Tue,Wed,Thu,Fri', entry)
    assert(entry.days == "Sun,Mon,Tue,Wed,Thu,Fri")
    entry = parse_rule_entry_line('InternetGatewayDevice.TimeRestriction.RestRules.1.TimeFrom=21:00', entry)
    assert(entry.time_from == "21:00")
    entry = parse_rule_entry_line('InternetGatewayDevice.TimeRestriction.RestRules.1.TimeTo=23:59', entry)
    assert(entry.time_to == "23:59")

def tes_parse_add_entry():
    entry = parse_add_entry('Username Mon,Tue 08:00-19:00')
    assert(entry.username == 'Username')
    assert(entry.days == 'Mon,Tue')
    assert(entry.time_from == '08:00') 
    assert(entry.time_to == '19:00') 
    

