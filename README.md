# mooc_spider
## 爬取慕课网的课程及其相关信息  

先运行get_schools.py获取mooc的大学数据，保存为schools.json，如下图  

<img width="600" alt="image" src="https://user-images.githubusercontent.com/77054680/232327122-f37651e8-bfbd-45d3-b62e-32bce09d8d29.png">

***

然后运行get_courses.py获取每所大学的课程数据，每所大学的所有课程单独保存为一个json文件。  
>请注意：  
>+ 运行前需要将页面中代码`for school in schools[:6]:`后面的中括号连同里面的内容删除，否则它将仅爬取6所大学对应的课程。  
>+ 一定要先执行get_schools.py，因为get_courses.py的执行需要读取前者的运行结果。

<img width="600" alt="image" src="https://user-images.githubusercontent.com/77054680/232327174-79561eaf-b7fc-44f6-b4d0-d9202fbfc37d.png">

***

接着运行get_course_comments.py获取每个课程下的评论数据，每个课程的所有评论单独保存为一个json文件。
>请注意：一定要先执行get_courses.py，因为get_course_comments.py的执行需要读取前者的运行结果。  

<img width="763" alt="image" src="https://user-images.githubusercontent.com/77054680/232327229-d3993635-e9a0-4462-8e9e-10b94a4c6cb9.png">
