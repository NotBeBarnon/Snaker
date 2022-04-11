# -*- coding:utf-8 -*-
# @Time        : 2021/12/30 15:46
# @Author      : Tuffy
# @Description : 贪吃蛇游戏
import typer

Application = typer.Typer()


@Application.command()
def run1(
        move: str = typer.Argument(..., help="参赛A队"),
        snack: str = typer.Argument(..., help="参赛B队"),
):
    # 校验目录是否存在
    from src.settings import PROJECT_DIR
    print(f"players/{move}/GenerateMove.py")
    move_file = PROJECT_DIR.joinpath(f"players/{move}/GenerateMove.py")
    snack_file = PROJECT_DIR.joinpath(f"players/{snack}/GenerateSnack.py")
    if not (move_file.exists() and snack_file.exists()):
        typer.echo("缺少比赛程序！")
        raise typer.Abort()

    from src.game_process import GameProcess, MoveProcess, SnackProcess
    from multiprocessing import Pipe

    move_conn_parent, move_conn_sub = Pipe()
    snack_conn_parent, snack_conn_sub = Pipe()
    game_process_ = GameProcess(move_conn_parent, snack_conn_parent, move)
    move_process_ = MoveProcess(move_conn_sub, f"players.{move}.GenerateMove")
    snack_process_ = SnackProcess(snack_conn_sub, f"players.{snack}.GenerateSnack")
    move_process_.start()
    snack_process_.start()
    game_process_.start()

    game_process_.join()


@Application.command()
def run2(
        player1: str = typer.Argument(..., help="贪吃蛇移动程序小队名称"),
        player2: str = typer.Argument(..., help="食物生成程序小队名称"),
):
    from src.settings import PROJECT_DIR
    move_file1 = PROJECT_DIR.joinpath(f"players/{player1}/GenerateMove.py")
    snack_file1 = PROJECT_DIR.joinpath(f"players/{player1}/GenerateSnack.py")
    move_file2 = PROJECT_DIR.joinpath(f"players/{player2}/GenerateMove.py")
    snack_file2 = PROJECT_DIR.joinpath(f"players/{player2}/GenerateSnack.py")
    if not (move_file1.exists() and snack_file1.exists() and move_file2.exists() and snack_file2.exists()):
        typer.echo("缺少比赛程序！")
        raise typer.Abort()

    from multiprocessing import Pipe
    from src.game_process import GameProcess, MoveProcess, SnackProcess

    move_conn_parent1, move_conn_sub1 = Pipe()
    snack_conn_parent1, snack_conn_sub1 = Pipe()
    game_process_1 = GameProcess(move_conn_parent1, snack_conn_parent1, player1)
    move_process_1 = MoveProcess(move_conn_sub1, f"players.{player1}.GenerateMove")
    snack_process_1 = SnackProcess(snack_conn_sub1, f"players.{player2}.GenerateSnack")
    move_process_1.start()
    snack_process_1.start()
    game_process_1.start()

    move_conn_parent2, move_conn_sub2 = Pipe()
    snack_conn_parent2, snack_conn_sub2 = Pipe()
    game_process_2 = GameProcess(move_conn_parent2, snack_conn_parent2, player2)
    move_process_2 = MoveProcess(move_conn_sub2, f"players.{player2}.GenerateMove")
    snack_process_2 = SnackProcess(snack_conn_sub2, f"players.{player1}.GenerateSnack")
    move_process_2.start()
    snack_process_2.start()
    game_process_2.start()

    game_process_1.join()
    game_process_2.join()


if __name__ == '__main__':
    Application()
