import osintkit.helper as kit_helper
import osintkit.whois as whois
import osintkit.geoip as geoip
import osintkit.iplookup as iplookup
import osintkit.arecord as arecord
import osintkit.screenshot as screenshot

import os

# This function is used to generate a report for a single data request
def single_report(input=None, function=None):
    report_data = ""
    data = f"<<<<<<<<<< {function.upper()} DATA FOR {input} >>>>>>>>>>" + "\n\n" + kit_helper.json_to_string(globals()[function].request(input))
    report_data += data
    return report_data

# This function is used to generate a report for multiple data requests - but only text output
def full_report(input=None, function=None):
    report_data = ""
    iplookup_data = f"<<<<<<<<<< IPLOOKUP DATA FOR {input} >>>>>>>>>>" + "\n\n" + kit_helper.json_to_string(iplookup.request(input))
    arecord_data = f"<<<<<<<<<< ARECORD DATA FOR {input} >>>>>>>>>>" + "\n\n" + kit_helper.json_to_string(arecord.request(input))
    geoip_data = f"<<<<<<<<<< GEOIP DATA FOR {input} >>>>>>>>>>" + "\n\n" + kit_helper.json_to_string(geoip.request(input))
    whois_data = f"<<<<<<<<<< WHOIS DATA FOR {input} >>>>>>>>>>" + "\n\n" + kit_helper.json_to_string(whois.request(input))
    report_data += iplookup_data + "\n" + arecord_data + "\n" + geoip_data + "\n" + whois_data
    return report_data

# This function is used to generate reports of requests that have file output
def file_output_report(input=None, function=None):
    return kit_helper.json_to_string(globals()[function].request(input))
