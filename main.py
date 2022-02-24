from asyncio import constants
from dataclasses import dataclass, field
import os
import sys
from types import TracebackType
from typing import Any, Union, List
from unittest import skipUnless


@dataclass
class Contributor:
    name: Any
    skills: Any = field(default_factory=list)

    def skill_from_role(self, role):
        for skill in self.skills:
            if skill.name == role.name and skill.level >= role.level:
                return skill

        return None

    def get_skill_level(self, skill_name):
        for skill in self.skills:
            if skill.name == skill_name:
                return skill.level
        return 0


@dataclass
class Role:
    name: Any
    level: int
    assignee: Union[Contributor, None] = None


@dataclass
class Skill:
    name: Any
    level: Any


@dataclass
class Project:
    name: Any
    duration: Any
    score: int
    best_before: Any
    roles: Any = field(default_factory=list)

    def is_fully_assigned(self):
        for project_role in self.roles:
            if project_role.assignee is None:
                return False

        return True


def load_input_data(input_file):
    with open(input_file, "r") as f:
        lines = f.readlines()

    n_contributors, n_projects = list(map(int, lines[0].split(" ")))

    contributors = []
    projects = []

    line_i = 1
    for _ in range(n_contributors):
        contributor_name, n_skills = lines[line_i].split(" ")
        n_skills = int(n_skills)
        contributor = Contributor(name=contributor_name)
        line_i += 1
        for _ in range(1, n_skills + 1):
            skill_name, skill_lvl = lines[line_i].split(" ")
            skill_lvl = int(skill_lvl)
            skill = Skill(name=skill_name, level=skill_lvl)
            contributor.skills.append(skill)
            line_i += 1
        contributors += [contributor]

    for _ in range(n_projects):
        (
            project_name,
            project_duration,
            project_score,
            project_best_before,
            n_roles,
        ) = lines[line_i].split(" ")
        project_duration = int(project_duration)
        project_score = int(project_score)
        project_best_before = int(project_best_before)
        n_roles = int(n_roles)
        project = Project(
            name=project_name,
            duration=project_duration,
            score=project_score,
            best_before=project_best_before,
        )
        line_i += 1
        for _ in range(n_roles):
            skill_name, skill_lvl = lines[line_i].split(" ")
            skill_lvl = int(skill_lvl)
            skill = Role(name=skill_name, level=skill_lvl)
            project.roles.append(skill)
            line_i += 1
        projects += [project]
    return contributors, projects


def score_projects(schedule):
    for project in schedule:
        contributors = []
        for role in project.roles:
            contributors += [role.assignee]
        roles = {role.name: role for role in project.roles}
        most_skilled_per_role = {role.name: None for role in project.roles}
        for role in project.roles:
            for contributor in contributors:
                skill_level = contributor.get_skill_level(role.name)
                if not most_skilled_per_role[
                    role.name
                ] or skill_level > most_skilled_per_role[role.name].get_skill_level(
                    role.name
                ):
                    most_skilled_per_role[role.name] = contributor
        # check if there is no assignee with level < skill - 1
        for role in project.roles:
            contributor_level = role.assignee.get_skill_level(role.name)
            if contributor_level < role.level - 1:
                print(
                    f"Project {project.name}: skill of assignee for role {role.name} is too low. ({role.level} required, found {contributor_level} for {role.assignee.name})"
                )
                return 0

        # check if low level assignee have a mentor
        for role_name, contributor in most_skilled_per_role.items():
            if roles[role_name].level - 1 == contributor.get_skill_level(role.name):
                potential_mentor = most_skilled_per_role[role.name]
                if (
                    potential_mentor.get_skill_level(role.name)
                    >= roles[role_name].level
                ):
                    print(f"{potential_mentor} is mentoring {contributor.name}.")
                else:
                    print(f"No mentor found for role {role.name}.")
                    return 0


def find_assignee_for_project_role(
    contributors: List[Contributor], project: Project, role: Role
):
    for contributor in contributors:
        skill = contributor.skill_from_role(role)

        if skill:
            return contributor

    return None


def generate_output_data(ordered_projects):
    with open("output.txt", "w") as f:
        f.write(str(len(ordered_projects)) + "\n")
        for project in ordered_projects:
            f.write(project.name + "\n")
            assignees = " ".join(
                list(map(lambda the_role: the_role.assignee.name, project.roles))
            )
            f.write(assignees + "\n")


if __name__ == "__main__":

    input_file_path = sys.argv[1]
    input_file_name = os.path.basename(input_file_path)

    contributors, projects = load_input_data(input_file_path)

    for project in projects:
        for role in project.roles:
            role.assignee = find_assignee_for_project_role(contributors, project, role)

    fully_assigned_projects = list(
        filter(lambda the_project: the_project.is_fully_assigned(), projects)
    )

    # generate_output_data(projects)
    print(fully_assigned_projects)
    score_projects(fully_assigned_projects)
