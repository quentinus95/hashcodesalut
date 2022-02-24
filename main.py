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
            print(f"{self.name} has skill {skill.name} but is not good enough ({skill.level} < {role.level})!")

            return None

        return skill

    def augment_skill(self, skill_name):
        previous_skill = self.skills[skill_name]

        print(f"Increasing {self.name}'s skill {skill_name} from {previous_skill.level} to {previous_skill.level + 1}")

        self.skills[skill_name] = Skill(name=previous_skill.name, level=previous_skill.level + 1)


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
        busy_contributors: List[Contributor] = []

        for role in self.roles:
            can_be_done = False
            for contributor in contributors:
                skill = contributor.skill_from_role(role)

                if skill:
                    if contributor in busy_contributors:
                        print(f"{contributor.name} is already involved in {project.name}; ignoring.")
                        continue

                    can_be_done = True
                    busy_contributors.append(contributor)
                    print(f"### Electing {contributor} for role {role} on {project.name}")
                    break

            if not can_be_done:
                print(f"Could not find a contributor for role {role}!")

                return False

        return True

    def assign_contributors(self, contributors: List[Contributor]):
        busy_contributors: List[Contributor] = []

        for role in self.roles:
            for contributor in contributors:
                skill = contributor.skill_from_role(role)
                if skill:
                    if contributor in busy_contributors:
                        continue

                    role.assignee = (contributor, skill)
                    busy_contributors.append(contributor)

                    if skill.level <= role.level:
                            contributor.augment_skill(skill.name)

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

    with open(OUTPUT_FILE, 'w') as f:
        f.write(str(len(ordered_projects)) + "\n")
        for project in ordered_projects:
            f.write(project.name + "\n")
            assignees = " ".join(list(map(lambda the_role: the_role.assignee[0].name, project.roles)))
            f.write(assignees + "\n")


if __name__ == "__main__":
    input_file_path = sys.argv[1]
    input_file_name = os.path.basename(input_file_path)

    contributors, projects = load_input_data(input_file_path)

    remaining_projects: List[Project] = projects
    assigned_projects: List[Project] = []

    remaining_projects_count = len(remaining_projects)
    while len(remaining_projects) > 0:
        for project in remaining_projects:
            if project.can_be_done_by_contributors(contributors):
                project.assign_contributors(contributors)
                assigned_projects.append(project)
                remaining_projects.remove(project)

        # No more assigned projects
        if remaining_projects_count == len(remaining_projects):
            break

        remaining_projects_count = len(remaining_projects)

    # This breaks the concept of skills "progression".
    # assigned_sorted_projects = assigned_projects.sort(key=lambda project: project.score)

    generate_output_data(assigned_projects)
