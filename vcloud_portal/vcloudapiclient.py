import requests
from json import load

class VCloudDirectorApiClient:
    def __init__(self, configuration, tokenmgr):
        self.base_url = configuration.get_baseurl()
        self.username = configuration.get_baseurl()
        self.tokenmgr = tokenmgr
        self.session = requests.Session()
        self.session.verify = False

    def org_filter_by_metadata(self, item):
        try:
            return item['metadata']['environment'] != 'production'
        except KeyError:
            return False
        
    def vdc_filter_by_metadata(self, item):
        # example: item['metadata']['environment'] == 'test'
        try:
            return True
        except KeyError:
            return False

    def vm_filter_by_metadata(self, item):
        try:
            return True
        except KeyError:
            return False

    def get_orgs(self):
        if self.tokenmgr.is_token_expired():
            self.tokenmgr.renew_token()
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/json;version=36.3'
            }
        endpoint = self.base_url+'/cloudapi/1.0.0/orgs?pageSize=100'
        response = self.session.get(endpoint, headers=request_headers).json()
        result = []
        for item in response['values']:
            item['id'] = item['id'].rsplit(":")[-1]
            result.append(item)
        return result


    def get_vdcs(self):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/json;version=36.3'
            }
        endpoint = self.base_url+'/cloudapi/1.0.0/vdcs?pageSize=100'

        response = self.session.get(endpoint, headers=request_headers).json()
        result = []
        for item in response['values']:
            item['id'] = item['id'].rsplit(":")[-1]
            result.append(item)
        return result


    def get_vapps(self, vdc_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vdc/'+vdc_id
        response = self.session.get(endpoint, headers=request_headers).json()

        # excluding every other resource not VM/vApp
        filtered = [item for item in response['resourceEntities']['resourceEntity'] if item['id'].split(":")[2] == 'vapp']

        result = []
        for item in filtered:
            item['id'] = item['id'].rsplit(":")[-1]
            result.append(item)
        
        return result


    def get_vms(self, vapp_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vApp/vapp-'+vapp_id
        response = self.session.get(endpoint, headers=request_headers).json()

        result = []
        for item in [item for item in response['children']['vm']]:
            result.append({'id': item['id'].rsplit(":")[-1], 'name': item ['name'], 'status': item['status']})
        return result


    def get_single_org(self, org_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/org/'+org_id
        return self.session.get(endpoint, headers=request_headers).json()


    def get_single_vdc(self, vdc_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vdc/'+vdc_id
        return self.session.get(endpoint, headers=request_headers).json()


    def get_single_vapp(self, vapp_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vApp/vapp-'+vapp_id
        return self.session.get(endpoint, headers=request_headers).json()


    def get_single_vm(self, vm_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vApp/vm-'+vm_id
        return self.session.get(endpoint, headers=request_headers).json()


    def get_screen_ticket(self, vm_id):
        temp = self.get_single_vm(vm_id)['href']
        vmid = temp.split("/")[-1][3:]
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vApp/vm-'+vmid+'/screen/action/acquireMksTicket'
        response = self.session.post(endpoint, headers=request_headers).json()
        result = {
            'host': response['host'],
            'port': response['port'],
            'ticket': response['ticket']
            }
        return result


    def reset_vm(self, vm_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vApp/vm-'+vm_id+'/power/action/reset'
        response = self.session.post(endpoint, headers=request_headers)
        return response.reason


    def poweron_vm(self, vm_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vApp/vm-'+vm_id+'/power/action/powerOn'
        response = self.session.post(endpoint, headers=request_headers)
        return response.reason


    def poweroff_vm(self, vm_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vApp/vm-'+vm_id+'/power/action/powerOff'
        response = self.session.post(endpoint, headers=request_headers)
        return response.reason


    def get_org_metadata(self, org_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/org/'+org_id+'/metadata'
        response = self.session.get(endpoint, headers=request_headers).json()
        metadata = dict((item['key'],item['typedValue']['value']) for item in response['metadataEntry'])
        return dict(sorted(metadata.items()))


    def get_vdc_metadata(self, vdc_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vdc/'+vdc_id+'/metadata'
        response = self.session.get(endpoint, headers=request_headers).json()
        metadata = dict((item['key'],item['typedValue']['value']) for item in response['metadataEntry'])
        return dict(sorted(metadata.items()))


    def get_vm_metadata(self, vm_id):
        request_headers = {
            'Authorization': f"Bearer {self.tokenmgr.get_token()}",
            'Accept': 'application/*+json;version=36.3'
            }
        endpoint = self.base_url+'/api/vApp/vm-'+vm_id+'/metadata'
        response = self.session.get(endpoint, headers=request_headers).json()
        metadata = dict((item['key'],item['typedValue']['value']) for item in response['metadataEntry'])
        return dict(sorted(metadata.items()))
