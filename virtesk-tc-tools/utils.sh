#!/bin/bash

# Copyright (c) 2013-2016, Adfinis SyGroup AG
#
# This file is part of Virtesk VDI.
#
# Virtesk VDI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Virtesk VDI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Virtesk VDI.  If not, see <http://www.gnu.org/licenses/>.


debug() {
	if [[ $DEVELOPER_MODE -eq 1 ]]; then
		echo DEBUG: $* 1>&2
	fi
}

error_msg() {
	echo ERROR: $* 1>&2
}

parse_cmdline() {
	argc=${#ARGV[@]}

	[[ $argc -eq 0 ]] && display_usage
	[[ ${ARGV[1]} = "-h" ]] && display_usage
	[[ ${ARGV[1]} = "--help" ]] && display_usage

	TC_RAW="${ARGV[0]}"
	debug TC_RAW = $TC_RAW

	index=1

	while [[ $index -lt $argc ]]; do
		debug argument $index: ${ARGV[index]}
		if [[ "${ARGV[index]}" = "--" ]]; then
			CMDLINE_AVAILABLE=1
			ssh_opts=( ${ARGV[@]:1:$((index-1))} )
			debug ssh_opts: ${ssh_opts[@]}
			
			# skip --
			let index++ 

			if [[ index -eq $argc ]]; then
				error_msg "-- specified, but no remote cmdline given."
				error_msg

				display_usage
			fi

			remote_cmdline=( ${ARGV[@]:index:$argc} )
			debug remote_cmdline: ${remote_cmdline[@]}
			
			break
		fi	
		let index++
	done

	if [[ $CMDLINE_AVAILABLE -eq 0 ]]; then
		ssh_opts=( ${ARGV[@]:1:$argc} )
		debug ssh_opts: ${ssh_opts[@]}
	fi
}

parse_cmdline_simple() {
	[[ $# -ne 1 ]] && display_usage
	[[ $1 = "-h" ]] && display_usage
	[[ $1 = "--help" ]] && display_usage
}

parse_cmdline_twoargument() {
	argc=${#ARGV[@]}

	[[ ${ARGV[1]} = "-h" ]] && display_usage
	[[ ${ARGV[1]} = "--help" ]] && display_usage
	[[ $argc -ne 2 ]] && display_usage
}

source_configfiles(){
	if [[ "x${AMOOTHEI_TC_TOOLS_CONF_DIR}" = "x" ]]; then
		AMOOTHEI_TC_TOOLS_CONF_DIR="/etc/virtesk-vdi"
	fi

	# Sourcing main configuration file
	MAIN_CONF_FILE="${AMOOTHEI_TC_TOOLS_CONF_DIR}/virtesk-tc-tools.conf"
	
	[[ -r "${MAIN_CONF_FILE}" ]] || {
		error_msg Cannot read main config file "${MAIN_CONF_FILE}"
		error_msg Aborting...
		error_msg
		display_usage
	}
		
	source "${MAIN_CONF_FILE}"

	# PROGNAME=$(basename $BASH_SOURCE)
	PROGNAME=$(basename $0)
	debug PROGNAME=${PROGNAME}

	IND_CONF_FILE="${AMOOTHEI_TC_TOOLS_CONF_DIR}/virtesk-tc-tools.conf.dir/${PROGNAME}.conf"
	[[ -r "${IND_CONF_FILE}" ]] && source "${IND_CONF_FILE}"

}

# Append $TC_DOMAIN if a short name (e.g. contains no "." or ":")
# is given.
process_thinclient_arg() {
	echo "${TC_RAW}" | egrep -q '\.|:'	
	if [[ $? -ne 0 ]]; then
		TC="${TC_RAW}.${TC_DOMAIN}"
	else
		TC="${TC_RAW}"
	fi
}


