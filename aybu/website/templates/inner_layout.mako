
<%inherit file="/template.mako"/>

<div id="content_wrapper">
	<div id="left">
		<%include file="/base/inner_menu.mako" />
	</div>
	<div id="right">
		<div id="content">
			${next.body()}
		</div>
	</div>
	<div class="reset"></div>
</div>
