<%def name="css()">
	${parent.css()}
	${self.css_link('/css/reset.css')}
	${self.css_link('/css/common.css')}
	${self.css_link('/css/header.css')}
	<style type="text/css" media="screen, projection">
		#header {
			% if c.node and len(c.node.banners) > 0:
			background-image: url(${c.node.banners[0].url});
			% else:
				<% banner = h.static_url("/uploads/images/%s" % c.settings.banner) %>
				% if banner:
				background-image: url(${banner});
				% endif
			% endif
			background-repeat: no-repeat;
			background-position: left top;
			width:	${c.settings.banner_width}px;
			height: ${c.settings.banner_height}px;
		}
		#header > h1 {
			<% logo = h.static_url("/uploads/images/%s" % c.settings.logo) %>
			% if logo:
			background-image: url(${logo});
			% endif
			width:	${c.settings.logo_width}px;
			height: ${c.settings.logo_height}px;
		}
	</style>
	${self.css_link('/css/footer.css')}
</%def>

<%def name="js()">
	${parent.js()}
	% if c.settings.debug == True:
	${self.js_link('/js/common.js')}
	% else:
	${self.js_link('/js/common.min.js')}
	% endif
</%def>

<%inherit file="/base/base_template.mako"/>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" >
    <%include file="/base/head.mako" args="final_title=self.final_title, css=self.css, js=self.js"/>
    <body>
		<div id="wrapper">
			<%include file="/header.mako" />

			<div id="info">
				<%include file="/base/path.mako" args="final_title=self.final_title"/>
				<hr />
				<%include file="/base/user.mako" />
			</div>

			${next.body()}

			<%include file="/footer.mako"/>
		</div>
		<%include file="/base/analytics.mako"/>
    </body>
</html>
