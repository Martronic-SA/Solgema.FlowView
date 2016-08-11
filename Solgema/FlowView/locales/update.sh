domain=Solgema.FlowView
../../../../../bin/i18ndude rebuild-pot --pot $domain.pot --merge $domain-extra.pot --create $domain ../
../../../../../bin/i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po
