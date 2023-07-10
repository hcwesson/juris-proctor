#!/usr/bin/env python
# This is a simple script that leverages GPT-4 to assist with the process of grading legal exams.
# DISCLAIMER: All generated output MUST be carefully reviewed by an Actual Human Bean™
#
# It's ineffecient, rigid, and context-heavy; it expects a prompt split into segments in the following structure:
#
#   exam_partN/prompt
#   ├── exam_q.txt                      ➔  Exam question
#   ├── response_post.txt               ➔  Post-input demarcation
#   ├── response_pre.txt                ➔  Pre-input demarcation
#   ├── rubric_legal_issues.txt         ➔  Rubric section
#   ├── rubric_structure.txt            ➔  Rubric section
#   ├── rubric_writing_requirement.txt  ➔  Rubric section
#   ├── system.txt                      ➔  System prompt
#   └── user_prompt.txt                 ➔  User prompt
#
# Essentially, this was written as a one-shot script - I'd be amazed if I can ever repurpose this in the future,
# let alone anyone else.

import os, glob, shutil
import json
import openai
import timeit

openai.api_key = os.getenv("OPENAI_API_KEY")
__thisdir = os.path.dirname(os.path.realpath(__file__))

response_dir = f'{__thisdir}/responses'
completed_dir = f'{__thisdir}/completed_responses'
prompt_dir = f'{__thisdir}/prompt'
output_dir = f'{__thisdir}/evaluations'

rubric_types = [
    'legal_issues',
    'structure',
    'writing_requirement'
]

gpt4_models = {
    'march_ckpt': 'gpt-4-0314',
    'june_ckpt': 'gpt-4-0613',
    'latest': 'gpt-4',
}


def load_student_responses():
    loaded_responses = {}
    for filename in os.listdir(response_dir):
        basename, ext = os.path.splitext(filename)
        print(f'Loaded response: "{basename}"')
        with open(f'{response_dir}/{filename}', 'r', encoding='utf-8') as f:
            loaded_responses[basename] = f.read()
    return loaded_responses


def move_completed_student_response(student_identifier):
    shutil.move(
        f'{response_dir}/{student_identifier}.txt',
        f'{completed_dir}/{student_identifier}.txt'
    )


def load_prompt_segments():
    loaded_prompt_segments = {
        'system': '',
        'response_pre': '',
        'response_post': '',
        'exam_q': '',
        'rubric_legal_issues': '',
        'rubric_structure': '',
        'rubric_writing_req': '',
        'user_prompt': '',
    }
    for filename in os.listdir(prompt_dir):
        basename, ext = os.path.splitext(filename)
        print(f'Loaded prompt segment: "{basename}"')
        with open(f'{prompt_dir}/{filename}', 'r', encoding='utf-8') as f:
            loaded_prompt_segments[basename] = f.read()
    return loaded_prompt_segments


def construct_messages_for_rubric(prompt_segs, student_response, rubric_type):
    p = prompt_segs
    return [
        {'role': 'system', 'content': p['system']},
        {
            'role': 'user',
            'content': (p['response_pre'] +
                        student_response +
                        p['response_post'] +
                        p['exam_q'] +
                        p[f'rubric_{rubric_type}'] +
                        p['user_prompt']),
        },
    ]


def process_response(student_response, prompt_segs):
    evaluations = {}
    process_ctime_start = timeit.default_timer()
    for rubric_type in rubric_types:
        print(f'\tEvaluating rubric component "{rubric_type}"...')
        rubric_ctime_start = timeit.default_timer()
        evaluation = openai.ChatCompletion.create(
            model=gpt4_models['latest'],
            messages=construct_messages_for_rubric(
                prompt_segs,
                student_response,
                rubric_type,
            )
        )
        rubric_ctime_stop = timeit.default_timer()
        print(f'\tFinished rubric component "{rubric_type}",  t={rubric_ctime_stop - rubric_ctime_start}s')
        evaluations[rubric_type] = evaluation['choices'][0]['message']['content']
    process_ctime_stop = timeit.default_timer()
    print(f'Assessment complete, t={process_ctime_stop - process_ctime_start}s')
    return evaluations


def snake_to_title(input_string):
    words = input_string.split('_')
    return ' '.join([w.title() for w in words])


if __name__ == '__main__':
    student_responses = load_student_responses()
    prompt_segments = load_prompt_segments()

    print('Beginning batch evaluation.\n')
    batch_ctime_start = timeit.default_timer()
    for student_identifier, student_response in student_responses.items():
        print(f'Now grading exam for student:\t{student_identifier}')
        exam_eval = process_response(student_response, prompt_segments)
        print(f'Writing output to "{output_dir}/{student_identifier}_out.txt"')
        with open(f'{output_dir}/{student_identifier}_out.txt', 'w', encoding='utf-8') as outfile:
            outfile.write(f'---- BEGIN ASSESSMENT: {student_identifier} ----\n\n'),
            for rubric_type in rubric_types:
                outfile.write(f'-- BEGIN RUBRIC section: {snake_to_title(rubric_type)} --\n')
                outfile.write(exam_eval[rubric_type])
                outfile.write(f'\n-- END RUBRIC section: {snake_to_title(rubric_type)} --\n\n')
            outfile.write(f'\n---- END ASSESSMENT: {student_identifier} ----\n')
        print(f'Moving completed response file to ./{completed_dir}/{student_identifier}.txt\n')
        move_completed_student_response(student_identifier)
    batch_ctime_stop = timeit.default_timer()
    print(f'Batch evaluation complete, t={batch_ctime_stop - batch_ctime_start}')
    print('\n\nSEE YOU SPACE COWBOY...\n\n')

