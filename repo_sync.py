# -*- coding: utf-8 -*-
"""
使用PyGithub库实现本地仓库与GitHub仓库同步功能
"""
import os
import subprocess
from typing import Optional

from github import Github
from github.Auth import Token

from commFunc import getEncryptKeys

# cSpell:ignoreRegExp /[^\s]{16,}/
# cSpell:ignoreRegExp /\b[A-Z]{3,15}\b/g
# cSpell:ignoreRegExp /\b[A-Z]\b/g

def get_git_repo_info(local_path: str) -> tuple[Optional[str], Optional[str]]:
    """
    获取本地Git仓库的远程origin信息

    Args:
        local_path (str): 本地仓库路径

    Returns:
        tuple[Optional[str], Optional[str]]: (owner, repo_name) 或 (None, None)
    """
    try:
        # 切换到仓库目录
        original_cwd = os.getcwd()
        os.chdir(local_path)

        # 获取远程origin URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True
        )

        remote_url = result.stdout.strip()
        os.chdir(original_cwd)

        # 解析GitHub仓库信息
        # 处理类似 https://github.com/owner/repo.git 或 git@github.com:owner/repo.git 的URL
        if "github.com/" in remote_url:
            # HTTPS URL
            repo_part = remote_url.split("github.com/")[-1]
        elif "github.com:" in remote_url:
            # SSH URL
            repo_part = remote_url.split("github.com:")[-1]
        else:
            return None, None

        # 移除 .git 后缀
        if repo_part.endswith(".git"):
            repo_part = repo_part[:-4]

        parts = repo_part.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]

    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
        return None, None

    return None, None


def sync_local_to_github(
    local_repo_path: str,
    github_token: str,
    target_owner: Optional[str] = None,
    target_repo: Optional[str] = None,
    branch: str = "main"
) -> bool:
    """
    同步本地Git仓库到GitHub仓库

    Args:
        local_repo_path (str): 本地仓库路径（当前目录: "./"）
        github_token (str): GitHub访问令牌
        target_owner (str, optional): 目标仓库所有者, 如果为None则从本地仓库获取
        target_repo (str, optional): 目标仓库名称, 如果为None则从本地仓库获取
        branch (str): 要同步的分支, 默认为main

    Returns:
        bool: 同步是否成功
    """
    try:
        # 切换到仓库目录
        original_cwd = os.getcwd()
        os.chdir(local_repo_path)
        print(f"切换到仓库目录: {local_repo_path}")

        # 获取远程仓库信息
        if target_owner is None or target_repo is None:
            owner, repo_name = get_git_repo_info(local_repo_path)
            if owner is None or repo_name is None:
                print("无法从本地仓库获取GitHub仓库信息")
                os.chdir(original_cwd)
                return False
            target_owner = target_owner or owner
            target_repo = target_repo or repo_name

        print(f"目标仓库: {target_owner}/{target_repo}")

        # 使用访问令牌进行身份验证
        auth = Token(github_token)
        g = Github(auth=auth)
        
        # 验证token是否有效
        try:
            user = g.get_user()
            print(f"GitHub认证成功，用户: {user.login}")
        except Exception as e:
            print(f"GitHub认证失败: {str(e)}")
            os.chdir(original_cwd)
            return False

        # 获取目标仓库
        try:
            target_repo_obj = g.get_repo(f"{target_owner}/{target_repo}")
            print(f"成功获取仓库信息: {target_repo_obj.full_name}")
        except Exception as e:
            print(f"无法获取仓库 {target_owner}/{target_repo}: {str(e)}")
            os.chdir(original_cwd)
            return False

        # 添加远程仓库（如果不存在）
        try:
            subprocess.run(
                ["git", "remote", "add", "github", f"https://github.com/{target_owner}/{target_repo}.git"],
                capture_output=True,
                check=True
            )
            print("添加远程仓库 'github'")
        except subprocess.CalledProcessError:
            # 远程仓库可能已存在, 尝试更新URL
            try:
                subprocess.run(
                    ["git", "remote", "set-url", "github", f"https://github.com/{target_owner}/{target_repo}.git"],
                    capture_output=True,
                    check=True
                )
                print("更新远程仓库 'github' URL")
            except subprocess.CalledProcessError as e:
                print(f"设置远程仓库URL失败: {e}")
                os.chdir(original_cwd)
                return False

        # 添加所有更改到暂存区
        try:
            subprocess.run(["git", "add", "."], capture_output=True, check=True)
            print("添加所有更改到暂存区")
        except subprocess.CalledProcessError as e:
            print(f"添加更改到暂存区失败: {e}")
            os.chdir(original_cwd)
            return False

        # 检查是否有更改需要提交
        try:
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"检查Git状态失败: {e}")
            os.chdir(original_cwd)
            return False

        if status_result.stdout.strip():
            # 有更改需要提交
            commit_message = "🔄 自动同步"
            try:
                subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, check=True)
                print(f"已提交更改: {commit_message}")
            except subprocess.CalledProcessError as e:
                # 可能没有更改需要提交
                commit_result = subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    capture_output=True,
                    text=True
                )
                if "nothing to commit" in commit_result.stderr:
                    print("没有需要提交的更改")
                else:
                    print(f"提交更改失败: {commit_result.stderr}")
                    os.chdir(original_cwd)
                    return False
        else:
            print("没有需要提交的更改")

        # 检查当前分支
        try:
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = branch_result.stdout.strip()
            print(f"当前分支: {current_branch}")
            
            if current_branch != branch:
                print(f"警告: 当前分支({current_branch})与目标分支({branch})不一致")
        except subprocess.CalledProcessError as e:
            print(f"获取当前分支信息失败: {e}")

        # 推送本地更改到GitHub
        print(f"正在推送更改到GitHub分支 '{branch}'...")
        push_result = subprocess.run(
            ["git", "push", "github", branch], 
            capture_output=True, 
            text=True
        )
        
        if push_result.returncode != 0:
            print(f"推送失败:")
            print(f"  返回码: {push_result.returncode}")
            print(f"  标准输出: {push_result.stdout}")
            print(f"  错误输出: {push_result.stderr}")
            
            # 检查是否有特定的错误信息
            error_output = push_result.stderr.lower()
            if "authentication" in error_output or "403" in error_output:
                print("  认证失败，请检查GitHub token是否正确且有推送权限")
            elif "could not resolve host" in error_output:
                print("  网络连接问题，无法连接到GitHub")
            elif "permission denied" in error_output:
                print("  权限被拒绝，请检查是否有推送权限")
            elif "nothing to push" in error_output or "already up to date" in push_result.stdout.lower():
                print("  没有需要推送的内容")
            
            os.chdir(original_cwd)
            return False
        else:
            print(f"成功推送更改到 GitHub 仓库 {target_owner}/{target_repo}")
            print(f"推送输出: {push_result.stdout}")

        print(f"成功将本地仓库 {local_repo_path} 同步到 GitHub 仓库 {target_owner}/{target_repo}")
        os.chdir(original_cwd)
        return True

    except subprocess.CalledProcessError as e:
        print(f"Git命令执行失败: {e}")
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
        return False
    except Exception as e:
        print(f"同步过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
        return False


def sync_github_to_local(
    local_repo_path: str,
    github_token: str,
    source_owner: Optional[str] = None,
    source_repo: Optional[str] = None,
    branch: str = "main"
) -> bool:
    """
    同步GitHub仓库到本地Git仓库

    Args:
        local_repo_path (str): 本地仓库路径（当前目录: "./")
        github_token (str): GitHub访问令牌
        source_owner (str, optional): 源仓库所有者, 如果为None则从本地仓库获取
        source_repo (str, optional): 源仓库名称, 如果为None则从本地仓库获取
        branch (str): 要同步的分支, 默认为main

    Returns:
        bool: 同步是否成功
    """
    try:
        # 切换到仓库目录
        original_cwd = os.getcwd()
        os.chdir(local_repo_path)

        # 获取远程仓库信息
        if source_owner is None or source_repo is None:
            owner, repo_name = get_git_repo_info(local_repo_path)
            if owner is None or repo_name is None:
                print("无法从本地仓库获取GitHub仓库信息")
                os.chdir(original_cwd)
                return False
            source_owner = source_owner or owner
            source_repo = source_repo or repo_name

        # 使用访问令牌进行身份验证
        auth = Token(github_token)
        g = Github(auth=auth)

        # 获取源仓库
        source_repo_obj = g.get_repo(f"{source_owner}/{source_repo}")

        # 添加远程仓库（如果不存在）
        try:
            subprocess.run(
                ["git", "remote", "add", "github", f"https://github.com/{source_owner}/{source_repo}.git"],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError:
            # 远程仓库可能已存在, 尝试更新URL
            subprocess.run(
                ["git", "remote", "set-url", "github", f"https://github.com/{source_owner}/{source_repo}.git"],
                capture_output=True,
                check=True
            )

        # 从GitHub拉取最新更改
        subprocess.run(["git", "pull", "github", branch], capture_output=True, check=True)

        print(f"成功将 GitHub 仓库 {source_owner}/{source_repo} 同步到本地仓库 {local_repo_path}")
        os.chdir(original_cwd)
        return True

    except Exception as e:
        print(f"同步过程中发生错误: {str(e)}")
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
        return False


def sync_local_to_github_repo():
    # 同步本地仓库到GitHub
    result = sync_local_to_github(LOCAL_REPO_PATH, GITHUB_TOKEN)

    return result


def sync_github_to_local_repo():
    # 同步GitHub到本地仓库
    result = sync_github_to_local(LOCAL_REPO_PATH, GITHUB_TOKEN)

    return result


GITHUB_TOKEN = getEncryptKeys('github_key')
LOCAL_REPO_PATH = "./"  # 本地仓库就是当前目录

if __name__ == "__main__":
    # 同步本地仓库到GitHub
    # sync_local_to_github(LOCAL_REPO_PATH, GITHUB_TOKEN)

    # 同步GitHub到本地仓库
    # sync_github_to_local(LOCAL_REPO_PATH, GITHUB_TOKEN)

    print("本地仓库与GitHub仓库同步工具")
    print("请从数据库中读取GITHUB_TOKEN")