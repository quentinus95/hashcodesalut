from dataclasses import dataclass, field
import os
import sys
from typing import Any, Union, List, Tuple, Dict

OUTPUT_FILE = "output.txt"


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

    def augment_skill(self, skill_name):
        previous_skill = self.skills[skill_name]

        self.skills[skill_name] = Skill(
            name=previous_skill.name, level=previous_skill.level + 1
        )

    def get_skill_level(self, skill_name):
        if skill_name in self.skills:
            return self.skills[skill_name].level
        else:
            return 0


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

    def can_be_done_by_contributors(self, contributors: List[Contributor]) -> bool:
        for role in self.roles:
            can_be_done = False
            for contributor in contributors:
                skill = contributor.skill_from_role(role)

                if skill:
                    can_be_done = True
                    break

            if not can_be_done:
                return False

        return True

    def assign_contributors(self, contributors: List[Contributor]):
        for role in self.roles:
            for contributor in contributors:
                skill = contributor.skill_from_role(role)
                if skill:
                    role.assignee = (contributor, skill)
                    improved_skill = Skill(name=skill.name, level=skill.level + 1)

                    contributor.skills[improved_skill.name] = improved_skill

                    break


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


def generate_output_data(ordered_projects: List[Project]):
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    with open(OUTPUT_FILE, "w") as f:
        f.write(str(len(ordered_projects)) + "\n")
        for project in ordered_projects:
            f.write(project.name + "\n")
            assignees = " ".join(
                list(map(lambda the_role: the_role.assignee[0].name, project.roles))
            )
            f.write(assignees + "\n")


def score_projects(schedule):
    score = 0
    finish_dates = {project.name: 0 for project in schedule}
    contributors_projects = {}

    for project in schedule:
        # find all contributors for this project
        contributors = []
        for role in project.roles:
            contributors += [role.assignee[0]]

        # find most skilled contributor for each skill
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
            contributor_level = role.assignee[0].get_skill_level(role.name)
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

        # compute the finish date of the project
        # check if contributor already working
        finish_date = project.duration
        max_date_contributors = 0
        for contributor in contributors:
            if contributor.name in contributors_projects:
                last_project = contributors_projects[contributor.name][-1]
                # print(
                #     f"Project {project.name}: {contributor.name} is already working on project {last_project} (which will finish at {finish_dates[last_project]})."
                # )
                if finish_dates[last_project] > max_date_contributors:
                    max_date_contributors = finish_dates[last_project]
        finish_date += max_date_contributors
        finish_dates[project.name] = finish_date

        if finish_date < project.best_before:
            project_score = project.score
        else:
            delay = finish_date - project.best_before
            project_score = max(0, project.score - delay)

        print(
            f"Project {project.name} will finish at {finish_date} (bbd was {project.best_before}), it earned {project_score} points (out of {project.score})."
        )

        score += project_score

        # update the list of projects of the contributors
        for contributor in contributors:
            if contributor.name not in contributors_projects:
                contributors_projects[contributor.name] = []
            contributors_projects[contributor.name] += [project.name]

    return score


if __name__ == "__main__":
    input_file_path = sys.argv[1]
    input_file_name = os.path.basename(input_file_path)

    contributors, projects = load_input_data(input_file_path)

    remaining_projects: List[Project] = projects
    assigned_projects: List[Project] = []

    remaining_projects_count = len(remaining_projects)
    while len(remaining_projects) > 0:
        next_project = remaining_projects.pop()

        if next_project.can_be_done_by_contributors(contributors):
            next_project.assign_contributors(contributors)
            assigned_projects.append(next_project)
        else:
            remaining_projects.append(next_project)

        # No more assigned projects
        if remaining_projects_count == len(remaining_projects):
            break

        remaining_projects_count = len(remaining_projects)

    # generate_output_data(assigned_projects)
    score = score_projects(assigned_projects)
    print(score)
