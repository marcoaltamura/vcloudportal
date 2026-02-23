from flask import Flask, render_template
from vcloud_portal.vcloudauth import *
from vcloud_portal.vcloudconfig import *
from vcloud_portal.vcloudapiclient import *

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# initialize Flask app
app = Flask(__name__)

try:
    cfg = VCloudDirectorConfiguration()
    tokenmgr = VCloudDirectorTokenManager(cfg.get_baseurl(), cfg.get_apitoken())
    instance = VCloudDirectorApiClient(cfg, tokenmgr)
except Exception as exc_msg:
    print(f"Unable to connect to vCloud Director! {exc_msg}")

@app.route('/')
def main_page():
    try:
        # retrieves the list of organizations in vCloud Director
        orgs = instance.get_orgs()
    except Exception as exc_msg:
        return render_template('error.html', error=exc_msg)
    
    for item in orgs:
        # retrieves tags associated to organization
        metadata = instance.get_org_metadata(item['id'])
        # adds metadata to the list
        item['metadata'] = metadata
    return render_template('list_orgs.html', orgs=filter(instance.org_filter_by_metadata,orgs))


@app.route('/org-<org_id>')
def org_info(org_id):
    try:
        # retrieves the informations about the organization selected
        org_info = instance.get_single_org(org_id)
    except:
        return render_template('error.html')
    
    org_name = org_info['name']
    org_fullname = org_info['fullName']
    org_description = org_info['description']
    # values field of the VDCs list
    vdcs = instance.get_vdcs()
    # for every vDC
    for item in vdcs:
        # retrieves tags associated to it
        metadata = instance.get_vdc_metadata(vdc_id=item['id'])
        # adds metadata to the list
        item['metadata'] = metadata
    # all vdcs according to the org_id
    org_vdcs = [{'id': item['id'], 'name': item['name'], 'description': item['description'], 'metadata': item['metadata']}
        for item in vdcs if item['org']['id'] == org_id]
    return render_template('list_vdcs.html', org_id=org_id, org_name=org_name, org_fullname=org_fullname,
                           org_description=org_description, vdcs=filter(instance.vdc_filter_by_metadata,org_vdcs))


@app.route('/org-<org_id>/vdc-<vdc_id>')
def vdc_info(org_id, vdc_id):
    try:
        # retrieves the informations about the vDC selected
        vdc_info = instance.get_single_vdc(vdc_id)
    except:
        return render_template('error.html')
    
    name = vdc_info['name']
    description = vdc_info['description']
    # retrieves all resources linked to actual vDC
    resources = instance.get_vapps(vdc_id)
    # retrieves tags associated to vDC
    metadata = instance.get_vdc_metadata(vdc_id)
    return render_template('list_resources.html', org_id=org_id, vdc_id=vdc_id, vdc_name=name,
                           description=description, resources=resources)


@app.route('/org-<org_id>/vdc-<vdc_id>/vapp-<vapp_id>')
def vapp_info(org_id, vdc_id, vapp_id):
    try:
        # retrieves the informations about the vApp selected
        vapp_info = instance.get_single_vapp(vapp_id=vapp_id)
    except:
        return render_template('error.html')
    
    name = vapp_info['name']
    description = vapp_info['description']
    # retrieves all resources linked to actual vDC
    vms = instance.get_vms(vapp_id=vapp_id)
    # for every vDC
    for item in vms:
        # retrieves tags associated to it
        metadata = instance.get_vm_metadata(vm_id=item['id'])
        # adds metadata to the list
        item['metadata'] = metadata
    return render_template('list_vms.html', org_id=org_id, vdc_id=vdc_id, vapp_id=vapp_id, vapp_name=name,
                           description=description, vms=vms)


@app.route('/org-<org_id>/vdc-<vdc_id>/vapp-<vapp_id>/vm-<vm_id>')
def vm_info(org_id, vdc_id, vapp_id, vm_id):
    try:
        # retrieves the informations about the single VM
        vm_info = instance.get_single_vm(vm_id=vm_id)
    except:
        return render_template('error.html')
    
    name = vm_info['name']
    description = vm_info['description']
    status = vm_info['status']
    # extracts the caption depending on the status code
    status = "Online" if status == 4 else "Offline" if status == 10 else "Unknown"
    # if status Online, retrieves the ticket hash for the console
    if status == "Online":
        data = instance.get_screen_ticket(vm_id)
    # else data about console are not retrieved
    else:
        data = False
    # retrieves tags associated to VM
    metadata = instance.get_vm_metadata(vm_id)
    return render_template('page_vm.html', data=data, vm_name=name, description=description, status=status, 
                           org_id=org_id, vdc_id=vdc_id, vapp_id=vapp_id, vm_id=vm_id, metadata=metadata)


@app.route('/org-<org_id>/vdc-<vdc_id>/vapp-<vapp_id>/vm-<vm_id>/reboot')
def vm_reboot(org_id, vdc_id, vapp_id, vm_id):
    try:
        # launches the reboot request for the selected VM
        instance.reset_vm(vm_id)
    except:
        return render_template('error.html')
    return '{"message": "VmReboot"}'


@app.route('/org-<org_id>/vdc-<vdc_id>/vapp-<vapp_id>/vm-<vm_id>/poweron')
def vm_poweron(org_id, vdc_id, vapp_id, vm_id):
    try:
        # launches the power-on request for the selected VM
        instance.poweron_vm(vm_id)
    except:
        return render_template('error.html')
    return '{"message": "VmPowerOn"}'


@app.route('/org-<org_id>/vdc-<vdc_id>/vapp-<vapp_id>/vm-<vm_id>/poweroff')
def vm_poweroff(org_id, vdc_id, vapp_id, vm_id):
    try:
        # launches the power-off request for the selected VM
        instance.poweroff_vm(vm_id)
    except:
        return render_template('error.html')
    return '{"message": "VmPowerOff"}'

if __name__ == "__main__":
    app.debug = False
    app.run()