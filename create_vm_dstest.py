---
# ----------------------------------------------------------
# Provisions VM(s) and creates DNS records
#
# AWX 1.0.5  v1.0.0
# ----------------------------------------------------------
- hosts: all
  gather_facts: false
  connection: local
  tasks:
  - name: Get reverse DNS name from IP
    command: echo "{{ ip_address | ipaddr('revdns') }}"
    register: revname

  - name: Get domain from hostname
    shell: echo "{{ inventory_hostname }}" | cut -d'.' -f 2,3
    register: domain

  - name: Get preferred datastore
    local_action: script /usr/bin/getDatastore.sh DaaS
    register: datastore

  - name: Show debug output
    debug:
      msg:
       - "inventory_hostname: {{ inventory_hostname }}"
       - "ip_address: {{ ip_address }}"
       - "revname: {{ revname.stdout }}"
       - "domain: {{ domain.stdout }}"
       - "datastore: {{ datastore.stdout }}"

  - name: Provision VM
    vmware_guest:
      hostname: "{{ vcenter_host }}"
      username: "{{ vcenter_user }}"
      password: "{{ vcenter_pass }}"
      name: "{{ inventory_hostname }}"
      folder: "{{ vcenter_folder }}"
      template: "{{ vcenter_template }}"
      cluster: "{{ vcenter_cluster }}"
      resource_pool: "{{ vcenter_resource_pool }}"
      datacenter: "{{ vcenter_datacenter }}"
      guest_id: "{{ vcenter_guestos }}"
      disk:
      - size_gb: "{{ vm_diskgb }}"
        type: "thick"
        datastore: "{{ datastore.stdout }}"
      networks:
      - name: "{{ network_name }}"
        ip: "{{ ip_address }}"
        gateway: "{{ gateway }}"
        domain: "{{ domain.stdout }}"
        netmask: "{{ netmask }}"
        dns_servers:
        - "{{ dns1 }}"
        - "{{ dns2 }}"
      customization:
        dns_servers:
        - "{{ dns1 }}"
        - "{{ dns2 }}"
        domain: "{{ domain.stdout }}"
        hostName: "{{ inventory_hostname }}"
        computerName: "{{ inventory_hostname }}"
      wait_for_ip_address: yes
      validate_certs: no
      state: present
    register: vmstatus

  - debug:
      msg: "Deploy message is: {{ vmstatus }}"

  - name: Add DNS records
    local_action: script /usr/bin/dns-add.sh {{ inventory_hostname }} {{ ip_address }} {{ revname.stdout }}

---
- hosts: all
  gather_facts: false
  connection: local
  tasks:
  - name: Show debug output
    debug:
      msg: "{{ datastore.stdout }}"
