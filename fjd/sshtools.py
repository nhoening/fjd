from getpass import getpass
import time
# ignore deprecation warnings that paramiko currently delivers
import warnings
warnings.simplefilter("ignore", DeprecationWarning)
import paramiko


'''
Tools for SSH communication: make client, send commands
'''

def ssh(client, cmd, ignore=[]):
    '''
    Run cmd on remote client (retry if connection fails), show errors (if we care about them)

    :params paramiko.SSHClient client:
    :params string cmd:
    :params string ignore: Error messages to ignore for this cmd
    :returns: stdout from host (minus some things we consider irrelevant)
    '''
    done = False
    while not done:
        try:
            stdin, stdout, stderr = client.exec_command(cmd)
            done = True
        except:
            time.sleep(4)
    err = stderr.read()
    dontcare_snippets = ['xset:', 'cannot remove']
    dontcare_snippets.extend(ignore)
    err_out = ""
    for e_line in err.split('\n'):
        yell_it = True
        for s in dontcare_snippets:
            if s in e_line:
                yell_it = False
        if yell_it and e_line != "":
            err_out += '%s\n' % e_line
    if err_out.strip() != "":
        print("[FJD] Error while doing stuff on server: {}".format(err_out))
    return stdout.read()


def mk_ssh_client(hostname, username):
    '''
    Make an SSH client and connect it.
    We first try a passwordless login, and then ask for credentials.

    :param string hostname: name of host
    :param string username: username on host
    :returns: paramiko.SSHClient if successful, None otherwise
    '''
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname, username=username)
    except (paramiko.AuthenticationException, paramiko.SSHException):
        print "[FJD] Could not connect to host '%s' as user '%s' with no password." % (hostname, username)
        print "          If you want password-less logon, please check your RSA key or shared/remembered connection setup."
    except Exception, e:
        print("[FJD] WARNING: Error while connecting with host {}: {}. ".format(hostname, e))
        if "Unknown server" in str(e):
            print "          Is it a known host (look in ~/.ssh/known_hosts)?"
        return None
    else:
        return ssh_client
    ssh_client = None
    while ssh_client is None:
        print("[FJD] Logging in user '{}' on host '{}' now (type 'exit' to abort): ".format(username, hostname))
        passwd = getpass()
        if passwd == 'exit':
            break
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        try:
            ssh_client.connect(hostname, username=username, password=passwd)
        except paramiko.AuthenticationException:
            print("[FJD] Authentication was not successful.")
            ssh_client = None
        except Exception, e:
            print("[FJD] WARNING: Error while connecting with host {}: {}".format((hostname, e)))
            ssh_client = None
    return ssh_client


