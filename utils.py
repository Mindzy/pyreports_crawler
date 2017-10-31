# -*- coding: utf-8 -*-


# improvement needed
def determine_obj_text(l_obj_text):
    # Determine whether text is context or not
    if l_obj_text.count('\n') * 10 * 3 < len(l_obj_text):
        return True
    return False


def context_cleaning(context):
    context = context.replace("\n", '')
    context = context.replace("\t", '')
    context = context.replace(' ', '')
    context = context.replace("\xef\x81\xae", '')
    context = context.replace("\xef\xbc\x89", ')')
    context = context.replace("\xef\xbc\x88", '(')
    context = context.replace("\xef\xbc\x9a", ':')
    context = context.replace("\xef\xbc\x8c", ',')
    context = context.replace("\xe2\x80\x94", '-')
    # replace pause mark
    context = context.replace("\xe3\x80\x81", '/')
    return context

