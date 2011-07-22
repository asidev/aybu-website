<%page args="i=0"/>
<div>${i}</div>
% if i:
<div><%include file="test_include.mako" args="i=i-1"/></div>
% endif
