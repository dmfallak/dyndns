mport boto3
import socket

route53 = boto3.client('route53')

def lambda_handler(event, context):
    # Get the ip of the caller
    ip = event["headers"]["X-Forwarded-For"]
    cur_ip = socket.gethostbyname("hostto.update.com")
    
    if ip == cur_ip:
        print "IP has not changed. Skipping record update. (%s == %s)" % (ip, cur_ip)
        return {"statusCode": 200, "body": '{"Success":"skipped update"}'}

    try:
        create_resource_record(get_zone_id("update.com"), "hostto", "update.com.", 'A', ip)
    except BaseException as e:
        return {"statusCode": 500, "body": "{\"Error\": \"%s\"" % (e)}
    
    return {"statusCode": 200, "body": '{"Success":"record updated"}'}

def create_resource_record(zone_id, host_name, hosted_zone_name, type, value):
    """This function creates resource records in the hosted zone passed by the calling function."""
    print 'Updating %s record %s in zone %s (%s)' % (type, host_name, hosted_zone_name, zone_id)
    if host_name[-1] != '.':
        host_name = host_name + '.'
    route53.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch={
                    "Comment": "Updated by Lambda DDNS",
                    "Changes": [
                        {
                            "Action": "UPSERT",
                            "ResourceRecordSet": {
                                "Name": host_name + hosted_zone_name,
                                "Type": type,
                                "TTL": 60,
                                "ResourceRecords": [
                                    {
                                        "Value": value
                                    },
                                ]
                            }
                        },
                    ]
                }
            )


def get_zone_id(zone_name):
    """This function returns the zone id for the zone name that's passed into the function."""
    if zone_name[-1] != '.':
        zone_name = zone_name + '.'
    hosted_zones = route53.list_hosted_zones()
    x = filter(lambda record: record['Name'] == zone_name, hosted_zones['HostedZones'])
    try:
        zone_id_long = x[0]['Id']
        zone_id = str.split(str(zone_id_long),'/')[2]
        return zone_id
    except BaseException as e:
        print e

