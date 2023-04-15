# mooc_spider
爬取慕课网的课程及其相关信息  

先运行get_schools.py获取大学列表，保存为schools.json，如下图  

<img width="584" alt="image" src="https://user-images.githubusercontent.com/77054680/232192542-b235440b-ce6d-43fb-bad5-67efa8d1eacb.png">

然后运行get_courses.py获取每所大学的课程列表，每所大学的课程列表单独保存为一个json文件。  
>请注意：  
>+ 运行前需要将页面中代码`for school in schools[:6]:`后面的中括号连同里面的内容删除，否则它将仅爬取5所大学对应的课程。  
>+ 一定要先执行get_schools.py，因为get_courses.py的执行需要读取前者的运行结果。

<img width="584" alt="IBF@@U_L6295Q%T%G 9B@LR" src="https://user-images.githubusercontent.com/77054680/232193818-400091b8-f573-4f31-bf56-ebce3404a2d9.png">




