<div id="footer">
	<p>
		Powered by
		<a href="${c.settings.reseller_link}" rel="external"
		   class="${c.settings.reseller_name.replace(' ','')}">
			${c.settings.reseller_name}
		</a>
		| Valid
		<a href="http://validator.w3.org/check?uri=referer" rel="external">
			XHTML
		</a>
		|
		<a href="http://jigsaw.w3.org/css-validator/check/referer" rel="external">
			CSS
		</a>
	</p>
	<div>
		${h.literal(c.settings.footer_info)}
	</div>
</div>
