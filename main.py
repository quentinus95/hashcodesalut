from dataclasses import dataclass, field
import os
import sys
from typing import Any, Union, List, Tuple, Dict



@dataclass(frozen=True)
class Skill:
    name: str
    level: int


@dataclass
class Contributor:
    name: Any
    skills: Dict[str, Skill] = field(default_factory=dict)

    def skill_from_role(self, role) -> Union[Skill, None]:
        if role.name not in self.skills:
            return None

        skill = self.skills[role.name]
        if skill.level < role.level:
            return None

        return skill


@dataclass
class Role:
    name: str
    level: int
    assignee: Union[Tuple[Contributor, Skill], None] = None


@dataclass
class Project:
    name: str
    duration: int
    score: int
    best_before: int
    roles: List[Role] = field(default_factory=list)

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
            contributor.skills[skill.name] = skill
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


def find_assignee_for_project_role(contributors: List[Contributor], project: Project, role: Role) -> Union[Tuple[Contributor, Skill], None]:
    for contributor in contributors:
        skill = contributor.skill_from_role(role)

        if skill:
            return contributor, skill

    return None


def generate_output_data(ordered_projects: List[Project]):
    with open('output.txt', 'w') as f:
        f.write(str(len(ordered_projects)) + "\n")
        for project in ordered_projects:
            f.write(project.name + "\n")
            assignees = " ".join(list(map(lambda the_role: the_role.assignee[0].name, project.roles)))
            f.write(assignees + "\n")


if __name__ == "__main__":

    input_file_path = sys.argv[1]
    input_file_name = os.path.basename(input_file_path)

    contributors, projects = load_input_data(input_file_path)

    for project in projects:
        for role in project.roles:
            role.assignee = find_assignee_for_project_role(contributors, project, role)

    fully_assigned_projects = list(filter(lambda the_project: the_project.is_fully_assigned(), projects))

    generate_output_data(fully_assigned_projects)
