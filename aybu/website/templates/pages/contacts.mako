<%def name="js()">
	${parent.js()}
	<script type="text/javascript">
		RecaptchaOptions.theme = 'white';
	</script>
</%def>

<%inherit file="/base/contacts_base_layout.mako"/>

<div id="editable_content">
	${h.literal(c.translation.content)}
</div>
<div>
	<%include file="/base/contacts_form.mako" />
</div>
