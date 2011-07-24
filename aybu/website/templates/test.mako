<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" >
    <body>
        <div>
            <ul>
                <li>ID: ${entity.id}</li>
                <li>Label: ${entity.label}</li>
                <li>Title: ${entity.title}</li>
                <li>Content: ${entity.content}</li>
            </ul>
        </div>
		<div><%include file="test_include.mako" args="i=10" /></div>
    </body>
</html>
