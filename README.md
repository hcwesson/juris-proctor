# juris-proctor
This is a simple script that leverages GPT-4 to assist with the process of grading legal exams. It's ineffecient, context-heavy, and rigid. I primarly wrote it for fun with the goal of providing a marginal speed boost to an otherwise tedious task (albeit at a very costly rate - those tokens ain't cheap!) 

This was essentially written as a one-and-done project, so I'd be amazed if I can use this again in the future - let alone anyone else.

> **DISCLAIMER:** All generated output MUST be carefully reviewed by an Actual Human Bean™

The script expects a prompt split into segments in the following structure:
```
  exam_partN/prompt
  ├── exam_q.txt                      ➔  Exam question
  ├── response_post.txt               ➔  Post-input demarcation
  ├── response_pre.txt                ➔  Pre-input demarcation
  ├── rubric_legal_issues.txt         ➔  Rubric section
  ├── rubric_structure.txt            ➔  Rubric section
  ├── rubric_writing_requirement.txt  ➔  Rubric section
  ├── system.txt                      ➔  System prompt
  └── user_prompt.txt                 ➔  User prompt
```
