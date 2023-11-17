/** @odoo-module **/
import { registry } from "@web/core/registry";
const { Component, useState, onWillStart, useRef } = owl
import { useService } from '@web/core/utils/hooks';


//Tạo 1 class extend component owl trên
export class ToDoListContainer extends Component {
    //Hàm setup khơi tạo quan trọng
    setup() {
        //khai báo state giá trị
        this.state = useState({
            task: { name: '', color: '#FFFFFF', completed: false },
            taskList: [],
            isEdit: false,
            activeId: false,
        })
        //khởi tạo 1 orm để lấy data....
        this.orm = useService("orm")
        this.model = 'owl.todo.list'
        this.searchinput = useRef("search-input")

        onWillStart(async () => {
            await this.GetAllTask()
        })
    }

    async GetAllTask() {
        this.state.taskList = await this.orm.searchRead(this.model, [], ["name", "color", "completed"])
    }

    addTask() {
        this.resetForm()
        this.isEdit = false
        this.activeId = false
    }

    editTask(task) {
        this.state.activeId = task.id
        this.state.isEdit = true
        //... mean lấy hết giá trị trong đó của task
        this.state.task = { ...task }
    }

    async saveTask() {
        if (!this.state.isEdit) {
            //ko là edit thì tạo
            await this.orm.create(this.model, [this.state.task])
        } else {
            //là edit thì chèn
            await this.orm.write(this.model, [this.state.activeId], this.state.task)
        }
        //refresh lại giá trị
        await this.GetAllTask()
    }

    async deleteTask(task) {
        await this.orm.unlink(this.model, [task.id])
        //refresh lại giá trị
        await this.GetAllTask()
    }

    resetForm() {
        this.state.task = { name: '', color: '#FFFFFF', completed: false }
    }

    async searchTasks() {
        //lấy giá trị của input
        const text = this.searchinput.el.value
        console.log(this.searchinput)
        console.log(text)
        this.state.taskList = await this.orm.searchRead(this.model, [['name', 'ilike', text]], ["name", "color", "completed"])
    }

    async ToggleCompleted(e,task) {
        await this.orm.write(this.model, [task.id], { completed: e.target.checked })
        //refresh lại giá trị
        await this.GetAllTask()
    }

    async updateColor(e, task) {
        await this.orm.write(this.model, [task.id], { color: e.target.value })
        //refresh lại giá trị
        await this.GetAllTask()
    }
}
//Khai báo giá trị của component trên
ToDoListContainer.template = 'owl.TodoList'
//gắn ('tag',component khai báo trên)
registry.category('actions').add('owl.action_todo_list_js', ToDoListContainer)