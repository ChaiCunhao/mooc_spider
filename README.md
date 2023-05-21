# mooc_spider
## 爬取慕课网的课程及其相关信息  

先运行get_schools.py获取mooc的大学数据，保存为schools.json，如下图  

<img width="300" alt="image" src="https://github.com/ChaiCunhao/mooc_spider/assets/77054680/aef34501-dab1-45d5-a566-64fc221e63b9">

***

然后运行get_courses.py获取每所大学的课程数据，每所大学的所有课程单独保存为一个json文件。
>请注意：  
>+ 运行前需要将页面中代码`for school in schools[:6]:`后面的中括号连同里面的内容删除，否则它将仅爬取6所大学对应的课程。  
>+ 一定要先执行get_schools.py，因为get_courses.py的执行需要读取前者的运行结果。

<img width="400" alt="image" src="https://github.com/ChaiCunhao/mooc_spider/assets/77054680/063e214e-293f-4e56-8e30-7a16e4d336b8">

***

接着运行get_course_comments.py获取每个课程下的评论数据，每个课程的所有评论单独保存为一个json文件。
>请注意：一定要先执行get_courses.py，因为get_course_comments.py的执行需要读取前者的运行结果。  

<img width="400" alt="image" src="https://github.com/ChaiCunhao/mooc_spider/assets/77054680/dd023f60-c6ec-4280-aca1-ecb1a4ab0d58">

***

然后运行get_course_comments.py获取每个评论者的用户数据。包括用户基本信息，学过的课程，发表的主题、回复、评论。
>请注意：一定要先执行get_course_comments.py获取评论数据。因为评论数据中含有用户Id，它是爬取用户数据所必需的。

<img width="400" alt="image" src="https://github.com/ChaiCunhao/mooc_spider/assets/77054680/abf8b2af-ddc7-482c-a345-a3ff94b7ec73">


