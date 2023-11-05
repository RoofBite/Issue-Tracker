# Issue-Tracker
![Issue-tracker-screenshot](https://user-images.githubusercontent.com/85451799/132257394-008c47b4-1aa6-4219-9ed1-00a11ed195c4.png)


##   Project is hosted on to AWS EC2 instance with EBS storage: https://bit.ly/roofbite-issue-tracker   <br>


**Project is in refactor process. Refactor state:**

- DONE - Pagination should be moved from the views to a separate function.
- DONE - The views.py file should be broken down into separate files for each category of view.
- IN PROGRESS - Simplifying if's logic 
- TO DO - HTTP response errors should be stored in variables for easy reuse.
- TO DO - Database queries should be extracted from the views and encapsulated in separate functions.


**Dependencies can be found in requirements.txt file**

## How to run project with Docker: <br>

- Value of variable secret_key in settings.py is stored in enviroment variable, it should be set before starting the project.
- Values of variables email and password in settings.py are also stored in enviroment variables, they should be properly set for password reset function to work.

- Then run commands in terminal: <br>
docker-compose build  <br>
docker run -p 8000:8000 issue-tracker

Go to: http://localhost:8000/sign-in/

Admin panel: http://localhost:8000/admin/

    login: admin
    password: admin

In admin panel you need to add two groups "developer" and "leader" for project to work properly.

## Project description

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
