#! /bin/bash
/usr/bin/wn $1 | grep "Information available for \(noun\|verb\|adj\|adv\) $1" | cut -d " " -f4
