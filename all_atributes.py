'''
logon types:'2': 'Interactive',
        '3': 'Network',
        '4': 'Batch',
        '5': 'Service',
        '7': 'Unlock',
        '8': 'NetworkCleartext',
        '9': 'NewCredentials',
        '10': 'RemoteInteractive',
        '11': 'CachedInteractive'
'''
'''
Time & Date Related:

timestamp (event time)
day_of_week
hour_of_day
date
is_business_hours
month
year
time_of_day

User & Account:

user (account name)
domain (user's domain)
user_sid (Security Identifier)
user_principal_name
account_type
user_flags
user_home_directory
user_script_path
user_profile_path
user_workstations

Session & Logon:

event_type (Logon/Logoff)
logon_type
logon_id
logon_process
session_id
session_name
session_duration
impersonation_level

System & Network:

computer (machine name)
source_ip
source_port
source_network_address
destination_ip
destination_port
network_address
workstation_name
terminal_services_session_id
virtual_account
restricted_admin_mode

Process & Security:

process_name
process_id
auth_package
package_name (authentication package)
key_length
status (success/failure)
sub_status (detailed status code)
failure_reason
error_code
elevated_token (yes/no)

Risk & Analysis:

risk_factors
risk_score
authentication_method
authentication_level
authentication_package_name
security_package_name
transited_services
authentication_information
certificate_information

Audit & Tracking:

event_id
event_record_id
event_sequence_number
event_category
event_task_category
keywords
correlation_id
audit_success
audit_failure

Additional Context:

target_user_name
target_domain_name
target_logon_id
target_server_name
target_info
caller_process_id
caller_process_name
group_membership
privileges_used

These fields can be extracted from various Event IDs (4624, 4625, 4634, 4647, 4648, etc.) though not all fields will be available for every event type. The exact fields available depend on:

The specific Event ID
Windows version
Audit policy settings
Type of logon/logoff event
Whether it's a success or failure event
'''