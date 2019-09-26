import paramiko
import argparse
import subprocess
import json

ROUTER_URL = '192.168.1.1'
ROOT_PATH = 'InternetGatewayDevice.TimeRestriction'
FORMAT_HELP = 'The format should be: username Mon,Tue,Wed,Thu,Fri,Sat 08:00-19:00'

is_verbose = False

class Entry:
    index = 0
    username = ''
    internet_allowed = False
    mac_address = ''
    days = ''
    time_from = ''
    time_to = ''

def print_entry(entry):
    print('Entry no. ' + str(entry.index))
    print("- Username:\t" + entry.username)
    print("- MAC Address:\t" + entry.mac_address)
    print("- Allowed:\t" + str(entry.internet_allowed))
    print("- Days:\t\t" + entry.days)
    print("- Time from:\t" + entry.time_from)
    print("- Time to:\t" + entry.time_to)

def get_entries():
    entries = []
    
    stdout = exec_command('cfgcmd get_idxes ' + ROOT_PATH + '.RestRules')
    output = stdout.read().decode()
    
    entries_idxes = output.split(' ')

    for i in entries_idxes:
        stdout = exec_command('cfgcmd get ' + ROOT_PATH + '.RestRules.' + i)
        entry = parse_rule_entry(int(i), stdout)
        entries.append(entry)

    return entries

def get_entry_by_index(entries, index):
    for entry in entries:
        if entry.index == index:
            return entry
    return None

def parse_rule_entry(index, entry_string):
    entry = Entry()
    entry.index = index

    for line in entry_string:
        entry = parse_rule_entry_line(line, entry)
        
    return entry

def parse_rule_entry_line(line, entry):
    if is_verbose:
        print('> Parsing rule entry ' + line)

    splitted = line.split('.')
    if len(splitted) != 5:
        raise ValueError('The line received does not have the expected section count of 5. Got ' + stdout.read().decode())

    if is_verbose:
        print('> Got line: ' + line)

    entryVar = splitted[len(splitted)-1].strip('\n')

    if not '=' in entryVar:
        raise ValueError('The = character is not in the entry variable. Might have received incorrect line.')

    splitted = entryVar.split('=')
    varName = splitted[0]
    varValue = splitted[1]
    if varName == 'InternetAllowed':
        if varValue == '1':
            entry.internet_allowed = True
        else:
            entry.internet_allowed = False
    elif varName == 'Username':
        entry.username = varValue
    elif varName == 'MACAddr':
        entry.mac_address = varValue
    elif varName == 'WeekDays':
        entry.days = varValue
    elif varName == 'TimeFrom':
        entry.time_from = varValue
    elif varName == 'TimeTo':
        entry.time_to = varValue

    return entry

def exec_command(command_string):
    if is_verbose:
        print('> Sending command string: ' + command_string)
        
    stdin, stdout, stderr = client.exec_command(command_string)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status > 0:
        raise ValueError('Error with exec_command. Returned exit_status of ' + str(exit_status))

    return stdout

def remove_entry(entry):
    index = entry.index
    cmd = 'ebtables -t filter -D TIME_RESTRICT -s ' + entry.mac_address + ' --timeblock ' + entry.time_from + '-' + entry.time_to + ' --weekdays ' + entry.days + ' -j DROP'
    exec_command(cmd)
    if is_verbose:
        print('> Sent ebtable delete command. ' + cmd);
        print('> ebtables -L is now: ' + exec_command('ebtables -L TIME_RESTRICT').read().decode())
    
    stdout = exec_command('sed -n /^' + str(index) + '\>/p /tmp/.timerestrict.rule')
    if is_verbose:
        print('> Removed entry from .timerestrict.rule if it exists')

    ## The following is the old code that runs the ebtables delete command taken from .timerestrict.rule
    ## There is no more need to run this because we have already removed it 
    # deleteLine = stdout.read().decode()
    # deleteLine = deleteLine[2:-1]
    # exec_command(deleteLine)
    
    if is_verbose:
        print('> Sent delete line: ' + deleteLine);

    cmd = 'sed -i /^' + str(index) + '\>/d /tmp/.timerestrict.rule'
    exec_command(cmd)
    if is_verbose:
        print('> Deleted timerestrict.rule entry. ' + cmd);

    cmd = 'cfgcmd del_obj ' + ROOT_PATH + '.RestRules.' + str(index)
    exec_command(cmd)
    if is_verbose:
        print('> Sent cfgcmd del_obj command. ' + cmd)

    print('> Done')

def parse_add_entry(entry_string):
    splitted = entry_string.split(' ')
    if len(splitted) != 3:
        raise ValueError('Incorrect entry format. ' + FORMAT_HELP)

    entry = Entry()
    entry.username = splitted[0]

    if j:
        entry.mac_address = j[entry.username]
        
    if not entry.mac_address:
        raise ValueError('Was not able to get the mac address for user ' + entry.username)

    days = splitted[1].split(',')
    for day in days:
        if len(day) != 3:
            raise ValueError('Error parsing the day. Expecting only three characters. Got ' + day)
        if day == 'Mon' or day == 'Tue' or day == 'Wed' or day == 'Thu' or day == 'Fri' or day == 'Sat' or day == 'Sun':
            entry.days = splitted[1]
        else:
            raise ValueError('Error parsing the days. Make sure that they are any of the following: "Mon, Tue, Wed, Thu, Fri, Sat, Sun". Got ' + day)

    times = splitted[2].split('-')
    if len(times) != 2:
        raise ValueError('Incorrect time format. Format should be: 08:00-18:00')

    entry.time_from = times[0]
    entry.time_to = times[1]
    if not ':' in entry.time_from or not ':' in entry.time_to:
        raise ValueError('The colon character was not found in entry.time_from or entry.time_to. Are you sure you are using the correct format: 08:00?')
    if len(entry.time_from) != 5 or len(entry.time_to) != 5:
        raise ValueError('The number of characters in entry.time_from or entry.time_to should be 5. Are you sure you are using the correct format: 08:00?')

    return entry

def add_entry_at_index(entry, index):
    if is_verbose:
        print('> Adding entry ' + entry.username + ' at index ' + str(index))

    cmd = 'ebtables -t filter -A TIME_RESTRICT -s ' + entry.mac_address + ' --timeblock ' + entry.time_from + '-' + entry.time_to + ' --weekdays ' + entry.days + ' -j DROP'
    exec_command(cmd)
    if is_verbose:
        print('> Sent ebtables add command. ' + cmd)
        print('> ebtables -L is now: ' + exec_command('ebtables -L TIME_RESTRICT').read().decode())

    cmd = 'cfgcmd add_obj ' + ROOT_PATH + '.RestRules.' + str(index)
    exec_command(cmd)
    if is_verbose:
        print('> Created the cfgcmd object. ' + cmd)

    allowed = '0'
    if entry.internet_allowed:
        allowed = '1'
    cmd = 'cfgcmd set ' + ROOT_PATH + '.RestRules.' + str(index) + '.InternetAllowed ' + allowed
    exec_command(cmd)
    if is_verbose:
        print('> Sent cfgcmd set InternetAllowed. ' + cmd)

    cmd = 'cfgcmd set ' + ROOT_PATH + '.RestRules.' + str(index) + '.Username ' + entry.username
    exec_command(cmd)
    if is_verbose:
        print('> Sent cfgcmd set Username. ' + cmd)

    cmd = 'cfgcmd set ' + ROOT_PATH + '.RestRules.' + str(index) + '.MACAddr ' + entry.mac_address
    exec_command(cmd)
    if is_verbose:
        print('> Sent cfgcmd set MacAddr. ' + cmd)

    cmd = 'cfgcmd set ' + ROOT_PATH + '.RestRules.' + str(index) + '.WeekDays ' + entry.days
    exec_command(cmd)
    if is_verbose:
        print('> Sent cfgcmd set Days. ' + cmd)

    cmd = 'cfgcmd set ' + ROOT_PATH + '.RestRules.' + str(index) + '.TimeFrom ' + entry.time_from
    exec_command(cmd)
    if is_verbose:
        print('> Sent cfgcmd set TimeFrom. ' + cmd)

    cmd = 'cfgcmd set ' + ROOT_PATH + '.RestRules.' + str(index) + '.TimeTo ' + entry.time_to
    exec_command(cmd)
    if is_verbose:
        print('> Sent cfgcmd set TimeTo. ' + cmd)
        
    print('Add entry for ' + entry.username + ' successful.')

def get_available_index(entries):
    indexes = []
    for entry in entries:
        indexes.append(entry.index)

    indexes.sort()
    i = 1
    for index in indexes:
        print(str(index) + " ?= " + str(i))
        if index != i and index > i:
            return i
        i = i + 1

    return indexes[len(indexes)-1] + 1

def enable_mode(is_enabled):
    cmd = ''
    if is_enabled:
        cmd = 'cfgcmd set ' + ROOT_PATH + '.Enable 1'
    else:
        cmd = 'cfgcmd set ' + ROOT_PATH + '.Enable 0'
    exec_command(cmd)
    if is_verbose:
        print('> Sent the command ' + cmd)

def main():
    global client
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-e',
                        '--enable',
                        help='Enable the parental control. Only accepts "0" or "1"',
                        action='store')
    parser.add_argument('-l',
                        '--list',
                        help='Lists the entries.',
                        action='store_true')
    parser.add_argument('-v',
                        '--verbose',
                        help='Logs verbosely.',
                        action='store_true')
    parser.add_argument('-d',
                        '--devices',
                        help='Specify path of the devices.json file to use',
                        action='store')
    parser.add_argument('-a',
                        '--add',
                        help='Add an entry. ' + FORMAT_HELP + '. This option should be passed along with "-d".',
                        action='store')
    parser.add_argument('-r',
                        '--remove',
                        help='Remove an entry by specifying the entry number.',
                        action='store')
    parser.add_argument('user',
                        help='The username to sign in using SSH.')
    parser.add_argument('password',
                        help='The password to sign in using SSH.')

    args = parser.parse_args()

    is_verbose = False
    if args.verbose:
        is_verbose = True

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.connect(ROUTER_URL, username=args.user, password=args.password)
    if is_verbose:
        print('Client connecting connect to ' + ROUTER_URL + ' with ' + args.user + ' and ' + args.password)

    if args.devices:
        with open(args.devices, 'r') as f:
            file_string = f.read()
            j = json.loads(file_string)

    entries = get_entries()
    if len(entries) <= 0:
        raise ValueError('There are no available entries.')


    if args.list:
        i = 0
        for entry in entries:
            print_entry(entry)
            print('')
            i = i + 1
    elif args.add:
        if not args.devices:
            raise ValueError('-a option should be run with -d.');

        entry = parse_add_entry(args.add)
        available_index = get_available_index(entries)
        entry.index = available_index

        if is_verbose:
            print('Adding entry')
            print_entry(entry)

        print('Available index is ' + str(available_index))
        add_entry_at_index(entry, available_index)
    elif args.enable:
        is_enabled = False
        if args.enable == '1':
            is_enabled = True
        enable_mode(is_enabled)
    elif args.remove:
        index = int(args.remove)
        entry = get_entry_by_index(entries, index)
        remove_entry(entry, index)

    client.close()

if __name__ == "__main__":
    main()
