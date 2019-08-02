from shodan import Shodan 
import requests
import json
import hackingtools as ht
from hackingtools.core import Logger, Config
import time
from colorama import init, Fore
import os

config = Config.getConfig(parentKey='modules', key='ht_shodan')
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))

class StartModule():

    api = None

    def __init__(self):
        Logger.printMessage(message='ht_shodan loaded', debug_core=True)
        self.settingApi()

    def help(self):
        Logger.printMessage(message=ht.getFunctionsNamesFromModule('ht_shodan'))
        
    def settingApi(self, shodanKeyString=None):
        try:
            if not shodanKeyString:
                shodanKeyString = config['api_key']
            Logger.printMessage(message='{methodName}'.format(methodName='settingApi'), description=shodanKeyString, debug_core=True)
            self.api = Shodan(shodanKeyString)
        except:
            Logger.printMessage(message='{methodName}'.format(methodName='settingApi'), description=config['bad_api_key_error'], debug_core=True, is_error=True) 

    def getIPListfromServices(self, serviceName, shodanKeyString=None):
        Logger.printMessage(message='{methodName}'.format(methodName='getIPListfromServices'), description='{param}'.format(param=serviceName), debug_module=True)
        if not self.api and not shodanKeyString:
            self.settingApi(Config.getApiKey('shodan_api'))
        if self.api or shodanKeyString:
            if shodanKeyString:
                self.settingApi(shodanKeyString=shodanKeyString)
            try:
                result = self.api.search(serviceName)
                dict_obj = []
                for res in result['matches']:
                    dict_obj.append(res['ip_str'].encode('utf-8').decode('utf-8'))
                return dict_obj
            except:
                return []
        else:
            return config['bad_api_key_error']

    def queryShodan(self, category=''):
        try:
            Logger.printMessage(message='{methodName}'.format(methodName='queryShodan'), debug_module=True)

            days_back = int(baseConfig.osintDays) + 1
            limit_date = (datetime.date.today() - datetime.timedelta(days=days_back)).strftime(config['search_limit_date_format'])
            search_term = 'category:{category} after:{time}'.format(category=category, time=limit_date)

            results = self.api.search(search_term, page=1)

            Logger.printMessage(message='{message_result}: {res}'.format(message_result=config['msg_result_found'], res=results['total']), debug_module=True)

            pages = results['total']/100

            if results['total']%100 > 0:
                pages += 1

                ip_list = []

                for n in range(1, pages+1):
                    if n > 1:
                        results = self.api.search(search_term, page=n)

                    Logger.printMessage(message='{msg_fetch_page} {num} of {pages}...'.format(msg_fetch_page=config['msg_fetch_page'], num=n, pages=pages), debug_module=True)

                    for result in results['matches']:
                        ip_list.append(result['ip_str'])

                return ip_list

            else:
                return []

        except shodan.APIError as e:
            Logger.printMessage(message='{error}: {error_msg}'.format(error=config['error'], error_msg=e), debug_module=True)
            return []

    def shodan_search_host(self, ip):
        res = {}
        try:
            Logger.printMessage(message='{methodName}'.format(methodName='shodan_search_host'), description='{param}'.format(param=ip), debug_module=True)
            host = self.api.host(ip)

            interesting_data = config['scan_interesting_data_keys']

            for posibe_data in interesting_data:
                try:
                    if host[posibe_data]:
                        if isinstance(host[posibe_data], dict):
                            if posibe_data in 'data':
                                res[posibe_data] = {}
                                res[posibe_data]['port'] = host[posibe_data]['port']
                                res[posibe_data]['data'] = host[posibe_data]['data']
                            else:
                                res[posibe_data] = host[posibe_data][0]
                        else:
                            res[posibe_data] = host[posibe_data]
                    elif host.get(posible_data):
                        res[posibe_data] = host.get(posible_data)
                except:
                    try:
                        if host.get(posible_data):
                            res[posibe_data] = host.get(posible_data)
                    except:
                        pass

        except Exception as e:
            Logger.printMessage(message='Warning: {0}... Retrying in 0,5 seconds...'.format(e), color=Fore.YELLOW, debug_module=True)
            time.sleep(0.4)
            return self.shodan_search_host(ip)
        return res

    def getSSLCerts(self, ip):
        res = {}
        try:
            Logger.printMessage(message='{methodName}'.format(methodName='getSSLCerts'), debug_module=True)
            for banner in api.stream.ports([443, 8443]):
                if 'ssl' in banner:
                    res['ssl'] = banner['ssl']
        except Exception as e:
            res['ssl'] = None
        return res

    def searchFromConfig(self, search='', keyword=''):
        if search != '' and keyword != '' and config[search]:
            Logger.printMessage(message='{methodName}'.format(methodName='searchFromConfig', description=search), debug_module=True)
            url = ("https://api.shodan.io/{search}&key={api}".format(search=config[search], api=self.api)).format(ip=keyword) # IP because config {ip}
            request = requests.get(url)
            txt = request.text
            return json.loads(txt)
        else:
            Logger.printMessage(message='{methodName}'.format(methodName='searchFromConfig', description='suggestions_cause_bad_search'), debug_module=True)
            sugg_conf = []
            res = {}
            for configuration in config:
                if configuration.startswith('shodan_'):
                    sugg_conf.append(configuration)
            res['search_options'] = sugg_conf
            return res