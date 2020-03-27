<h1>Assemble</h1>

<p> Assemble is an application that supports the top-down development of applications. Users can create projects, refine their projects into smaller projects and create to do lists for those smaller projects. If any of your friends are working with you on the project they can be added into the workflow. </p>

<h3> How to get Assemble running</h3>
<ul>
  <li> Create a directory with this structure
    <p>project</p>
      --project_clone --> clone into this folder.
  </li>
  <li> Clone the repo into project_clone </li>
  <li> Create a virutal environment using virtualenv in the root directory </li>
  <li> Activate the virtual environment </li>
  <li> change directory into project_clone </li>
  <li> pip install -r requirements.txt </li>
  <li> Check if everything is running properly by running : python manage.py test assemble/tests </li>
  <li> python manage.py runserver </li>
  <li> Assemble should be open on port:8000 </li>
