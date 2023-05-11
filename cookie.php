<?php
if (isset($_GET['search'])) 
{
  $results = search_database($_GET['search']);
  echo 'Results for "'.$_GET['search'].'":<br/>';
  foreach ($results as $result)
  {
    echo $result['result']."<br/>";
  }
}
?>
