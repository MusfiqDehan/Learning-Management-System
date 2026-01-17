from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import Course, Lesson, Progress
from .forms import CourseForm, LessonForm


def course_list(request):
    courses = Course.objects.all()
    return render(request, "courses/course_list.html", {"courses": courses})


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    context = {"course": course}
    if request.user.is_authenticated and request.user in course.students.all():
        context["completed_lessons"] = Progress.objects.filter(
            student=request.user, lesson__course=course, completed=True
        )
    return render(request, "courses/course_detail.html", context)


@login_required
def course_create(request):
    if not request.user.is_instructor:
        raise PermissionDenied()
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect("course_list")
    else:
        form = CourseForm()
    return render(request, "courses/course_form.html", {"form": form})


@login_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.user != course.instructor or not request.user.is_instructor:
        raise PermissionDenied()
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect("course_list")
    else:
        form = CourseForm(instance=course)
    return render(request, "courses/course_form.html", {"form": form})


@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.user != course.instructor or not request.user.is_instructor:
        raise PermissionDenied()
    if request.method == "POST":
        course.delete()
        return redirect("course_list")
    return render(request, "courses/course_confirm_delete.html", {"course": course})


@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.user not in course.students.all():
        course.students.add(request.user)
    return redirect("course_detail", pk=pk)


@login_required
def lesson_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.user == course.instructor or request.user in course.students.all():
        lessons = course.lessons.all()
        return render(
            request, "lessons/lesson_list.html", {"course": course, "lessons": lessons}
        )
    return redirect("course_list")


@login_required
def lesson_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.user != course.instructor:
        raise PermissionDenied(
            "You don't have permission to add lessons to this course."
        )
    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            return redirect("course_detail", pk=course_pk)
    else:
        form = LessonForm()
    return render(request, "lessons/lesson_form.html", {"form": form, "course": course})


@login_required
def lesson_update(request, course_pk, pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=pk, course=course)
    if request.user != course.instructor:
        raise PermissionDenied()
    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect("course_detail", pk=course_pk)
    else:
        form = LessonForm(instance=lesson)
    return render(request, "lessons/lesson_form.html", {"form": form, "course": course})


@login_required
def lesson_delete(request, course_pk, pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=pk, course=course)
    if request.user != course.instructor:
        raise PermissionDenied()
    if request.method == "POST":
        lesson.delete()
        return redirect("course_detail", pk=course_pk)
    return render(request, "lessons/lesson_confirm_delete.html", {"lesson": lesson})


@login_required
def lesson_detail(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)
    if request.user == course.instructor or request.user in course.students.all():
        progress, created = Progress.objects.get_or_create(
            student=request.user, lesson=lesson
        )
        course_completed = course.is_completed
        course_completed_at = course.completed_at
        return render(
            request,
            "lessons/lesson_detail.html",
            {
                "course": course,
                "lesson": lesson,
                "progress": progress,
                "course_completed": course_completed,
                "course_completed_at": course_completed_at,
            },
        )
    return redirect("course_list")


@login_required
def mark_lesson_complete(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)
    if request.user in course.students.all():
        progress, created = Progress.objects.get_or_create(
            student=request.user, lesson=lesson
        )
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        course.update_completion_status(request.user)
    return redirect("lesson_detail", course_pk=course_pk, lesson_pk=lesson_pk)
