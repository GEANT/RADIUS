# CSI-anonymise.pl
#
# Copyright (c) 2014 Hans Berggren <hansb at kth.se>, IT Department, KTH Royal Institute of Technology
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# This script for Freeradius 2.2 and 3.0 anonymizes the MAC address which is sent in the eduroam f-ticks log.
# It is based on the function in radsecproxy (https://software.uninett.no/radsecproxy/)
# and the radiator-fticks-anonymizer by Johan Carlquist <jocar at su.se>
# (https://github.com/stockholmuniversity/radiator-fticks-anonymizer/blob/master/fticks_anonymizer)
# Use it with Freeradius with perl extension. Tested with FR 2.2.8 and 3.0.11
# Unfortunatly FR 2.1.x module linelog doesn't support syslog's facility argument.
# So, if you run FR 2.1.x you have to filter syslog message to grep fticks logs 
# and send to desired syslog server.
#
# Hans Berggren, KTH Royal Institute of Technology, Stockholm, Sweden
# <hansb at kth.se>
#
# To use this script:
# the Freeradius config directory (eg. /etc/raddb/) is here called ${confdir}.
#
# For vers.2.2 and vers. 3.0
# In the file ${confdir}/dictionary add:
# ATTRIBUTE  X-Calling-Station-Id  3000  string
# ATTRIBUTE  X-Realm               3001  string
#
# For FR vers. 2.2
# Copy this script to new file ${confdir}/CSI-anonymise.pl
# In the directory ${confdir}/modules/ do following:
# cp -p perl CSI_anonymise
# edit the file CSI_anonymise:
# change the line "perl {" to "perl CSI_anonymise {"
# change the line "module = ${confdir}/example.pl"" to "module = ${confdir}/CSI-anonymise.pl"
#
# For FR vers. 3.0
# Copy this script to new file ${confdir}/mods-config/perl/CSI-anonymise.pl
# In the directory ${confdir}/mods-enabled/ create a file named CSI_anonymise with following content:
# perl CSI_anonymise {
#   filename = ${modconfdir}/perl/CSI-anonymise.pl
# }
#
# For both vers. 2.2 and vers. 3.0
# in the file ${confdir}/sites-enabled/default in section post-auth add after reply_log:
#   CSI_anonymise
#   if (ok) {
#     f_ticks
#   }
# and insert the same also in the same section under Post-Auth-Type REJECT
#
# Follow the instructions on
# https://wiki.geant.org/display/H2eduroam/How+to+deploy+eduroam+on-site+or+on+campus#Howtodeployeduroamon-siteoroncampus-F-Ticks
# to configure module f_ticks. Change "%{Realm}" to "%{control:X-Realm}" and
# "%{Calling-Station-Id}" to "%{control:X-Calling-Station-Id}"
#
# Set the constants KEY and HASH_ALL below.
#
use strict;
use vars qw(%RAD_REQUEST %RAD_REPLY %RAD_CHECK);
use Data::Dumper;
use Digest::SHA qw(hmac_sha1_hex);

# %RAD_REQUEST; This hash holds original request from radius.
# %RAD_REPLY; In this hash you add values that will be returned to NAS.
# %RAD_CHECK; This is for check items. You can get or set values from/to control.

# Settings for your IdP. Use your own values.
use constant KEY => "YOUR HASH KEY HERE";
use constant HASH_ALL => 0; # Set to 1 if you want to hash the whole MAC address (including vendor part).
use constant MY_REALM => ""; # Set your IdP's realm here if you want to log users without realm in their identity. Use with care.
                             # Should not be necessary to set. See notes below.

# This is the remapping of return values
use constant    RLM_MODULE_REJECT=>    0;#  /* immediately reject the request */
use constant	RLM_MODULE_FAIL=>      1;#  /* module failed, don't reply */
use constant	RLM_MODULE_OK=>        2;#  /* the module is OK, continue */
use constant	RLM_MODULE_HANDLED=>   3;#  /* the module handled the request, so stop. */
use constant	RLM_MODULE_INVALID=>   4;#  /* the module considers the request invalid. */
use constant	RLM_MODULE_USERLOCK=>  5;#  /* reject the request (user is locked out) */
use constant	RLM_MODULE_NOTFOUND=>  6;#  /* user not found */
use constant	RLM_MODULE_NOOP=>      7;#  /* module succeeded without doing anything */
use constant	RLM_MODULE_UPDATED=>   8;#  /* OK (pairs modified) */
use constant	RLM_MODULE_NUMCODES=>  9;#  /* How many return codes there are */

# Same as src/include/radiusd.h
use constant	L_DBG=>   1;
use constant	L_AUTH=>  2;
use constant	L_INFO=>  3;
use constant	L_ERR=>   4;
use constant	L_PROXY=> 5;
use constant	L_ACCT=>  6;


# Function to handle post_auth where fticks are set.
sub post_auth {
	# Handle realm. If no realm attribute, do nothing. 
	# If realm is "DEFAULT" then proxy.conf is wrongly configured.
	# Change "realm DEFAULT" in it to realm "~.+$"
	# If realm is NULL add, if desired, your realm. This case can happen if user
	# doesn't have the realm in their outer identity. Use with care. It can be
        # an external user that has a misconfigured supplicant, not your user.
        # See MY_REALM above.
	my $realm = $RAD_REQUEST{'Realm'};
	if (!$realm) {
	    return RLM_MODULE_NOOP;
	}
	elsif ($realm eq "NULL") {
	    if (MY_REALM ne "") {
	        $RAD_CHECK{'X-Realm'} = MY_REALM;
	    } else {
	        return RLM_MODULE_NOOP;
	    }
	}
	elsif ($realm eq "DEFAULT") {
	    return RLM_MODULE_NOOP;
	}
	else {
	    $RAD_CHECK{'X-Realm'} = $realm;
	}

	# Anonymize the MAC address. If HASH_ALL is true then hash the whole MAC address.
	# If not, hash the second half of it and keep the vendor part in the anonymized MAC.
	my $csi = $RAD_REQUEST{'Calling-Station-Id'};
	$csi = lc("$csi");
	$csi =~ s/[^[:xdigit:]]//g;
	if (length($csi) != 12){
	    return RLM_MODULE_NOOP;
	}
	if (HASH_ALL) {
	    $csi = hmac_sha1_hex($csi, KEY);
        }
	else {
	    $csi =~ m/^(.{2})(.{2})(.{2})(.{6})$/; 
	    my $first_half = "$1" . ":" . "$2" . ":" . "$3" . ":" ;
	    $csi =~ /(.{6})$/;
	    my $second_half = $1;
	    $csi = "$first_half" . hmac_sha1_hex($second_half, KEY);
	}	
	$RAD_CHECK{'X-Calling-Station-Id'} = $csi;
	return RLM_MODULE_OK;
}
