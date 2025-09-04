#!/bin/bash

PY_BIN_LS=$(ls /usr/bin | grep -e "^python[\.0-9]*$")
p_versions=()
py_bins=()

for curr in $PY_BIN_LS; do
	version=$("/usr/bin/${curr}" --version)
	version_tmp=$(echo "$version" | cut --delimiter " " --fields 2)
	p_versions+=($version_tmp)
	py_bins+=($curr)
done

#echo ${py_bins[@]}
#echo ${p_versions[@]}

function list_versions () {
	if [[ ! $(is_version_available "python") ]]; then
		echo "Current $(python --version)"
		echo "-----------------------------"
	fi

	for i in ${!p_versions[@]}; do
		if [[ "${py_bins[i]}" == "python" ]]; then
			echo "Current $(python --version)"
			echo "-----------------------------"
		else
			echo "${py_bins[i]} - ${p_versions[i]}"
		fi
	done
}

function help() {
	echo "pvm is a package to help you to change between versions of python"
	echo "options:"
	echo "- use: 		[pvm use VERSION]	Change the current version"
	echo "- current: 	[pvm current]		Show the current version"
	echo "- list:		[pvm list]		Show all versions available"
	echo "- has: 		[pvm use ]		Verify if some version is available"
	echo "-----------------------------"
	list_versions
	return 0
}

function is_version_available() {
	if [[ " ${py_bins[@]} " =~ "$1" && "$1" != "" ]]; then
		return 0;
	fi

	return 1;
}

function switch_version() {
	if is_version_available $1; then
		if [[ $1 == "python" ]];then
			echo "ERROR: Version cannot be 'python'"
			return 1
		fi
	
		sudo ln -sf "/usr/bin/$1" "/usr/local/bin/python"
		list_versions $1

		return 0
	else
		echo "ERROR: Version $1 unavailable"
		echo "-----------------------------"
		list_versions
		return 1
	fi
}

function main () {
	if [[ " $@ " =~ "--help" ]]; then
		help
		return 0
	fi

	case $1 in
		"list")
			list_versions
			;;
		"current")
			echo "Current - $(python --version)"
			echo "-----------------------------"
			echo $(ls -l /usr/local/bin/python)
			;;
		"use")
			if switch_version $2; then
				return 0;
			else
				return 1;
			fi
			;;
		"has")
			if is_version_available $2; then
				echo "true"
			else
				echo "false"
			fi
			;;
		*)
			help
			;;
	esac

	return 0
}

main $1 $2
