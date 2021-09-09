# Issue-Tracker
<p><span style="font-size:1.2em">This is a fully functional <strong>issue tracker</strong> project, there are
            <strong>3
                groups</strong> of users: <span style="color:#2ecc71"><strong>admin</strong></span>, <span
                style="color:#c0392b"><strong>leader</strong></span>, and <span
                style="color:#3498db"><strong>developer</strong></span>.<br /><strong>Main features:</strong></span></p>
    <ul>
        <li>
            <p><span style="font-size:1.2em">Adding <strong>new</strong> <strong>issues</strong>.</span></p>
        </li>
        <li>
            <p><span style="font-size:1.2em">Adding <strong>comments </strong>to issues by leaders and developers in
                    projects.</span></p>
        </li>
        <li>
            <p><span style="font-size:1.2em">Seeing <strong>details </strong>of issues and <strong>history of
                        changes</strong>.</span></p>
        </li>
        <li>
            <p><span style="font-size:1.2em">Seeing the list of <strong>all issues</strong> in projects and <strong>issues
                        assigned to the user</strong>.</span></p>
        </li>
        <li>
            <p><span style="font-size:1.2em">Seeing <strong>separate </strong>lists of <strong>active </strong>and
                    <strong>old </strong>issues.</span></p>
        </li>
        <li>
            <p><span style="font-size:1.2em"><strong>Apply</strong> for <strong>projects </strong>and join them.</span>
            </p>
        </li>
        <li>
            <p><span style="font-size:1.2em">
                    Option of <strong>resigning </strong>from <strong><span style="color:#3498db">developer
                        </span></strong>and <strong><span style="color:#c0392b">leader </span></strong>position in
                    project.</span></p>
        </li>
    </ul>
    <p><span style="font-size:1.2em"><strong><span style="color:#c0392b">
                    Leader </span>features:</strong></span></p>
    <ul>
        <li>
            <p><span style="font-size:1.2em">The Leader can <strong>manage a list of developers </strong>in the project.</span>
            </p>
        </li>
        <li>
            <p><span style="font-size:1.2em">The Leader can <strong><span style="color:#2ecc71">accept </span></strong>and
                    <strong><span style="color:#c0392b">deny </span></strong>the developer's <strong>applications to the
                        project</strong>.</span></p>
        </li>
        <li>
            <p><span style="font-size:1.2em">The Leader can <strong>edit </strong>reported <strong>issues</strong>.</span>
            </p>
        </li>
    </ul>
    <p><span style="font-size:1.2em"><strong><span style="color:#2ecc71">Admin </span>features:</strong></span></p>
    <ul>
        <li>
            <p><span style="font-size:1.2em">Admin can&nbsp;<strong><span style="color:#2ecc71">accept
                        </span></strong>and
                    <strong><span style="color:#c0392b">deny&nbsp;</span>developer's </strong>and <strong>leader's
                    </strong>applications to the project.</span></p>
        </li>
        <li>
            <p><span style="font-size:1.2em">Admin can see <strong>list </strong>of issues in <strong>all
                        projects</strong>.</span></p>
        </li>

**Live version: http://issue-tracker-roofbite.herokuapp.com/sign-in/**

**Dependencies can be found in requirements.txt file**

## How to run project with Docker: <br>

- Value of variable secret_key in settings.py is stored in enviroment variable, it should be set before starting the project.
- Values of variables email and password in settings.py are also stored in enviroment variables, they should be properly set for password reset function to work.

- Then run commands in terminal: <br>
docker-compose build  <br>
docker run -p 8000:8000 issue-tracker

- Create superuser in project,
- (username="roofbite", is_superuser=True) stands for superadmin user,
change this query in forms.py and views.py for your superuser username.

