/** @odoo-module */

import { registry } from "@web/core/registry"
import { KpiCard } from "../kpi_card/kpi_card"
import { ChartRenderer } from "../chart_renderer/chart_renderer"
import { loadJS } from "@web/core/assets"
import { useService } from '@web/core/utils/hooks';
const { Component, onWillStart, useRef, onMounted, useState } = owl
//lấy color không bị trùng
import { getColor } from "@web/views/graph/colors"
//this will select the current web right now
var session = require('web.session');
//reload page
import { browser } from "@web/core/browser/browser"
import { routeToUrl } from "@web/core/browser/router_service"

export class OwlProjectDashboard extends Component {
    //Top Project (5 project limit)
    async getTopProject() {
        let domain = []
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const data = await this.orm.readGroup(this.model, domain, ['project_id'], ['project_id'], { limit: 5, orderby: "create_date desc" })
        const project_data = await this.orm.searchRead('project.ansv', [], ['color'])
        // console.log(data)
        const color = ['#dadada', '#f06050', '#f4a460', '#f7cd1f', '#6cc1ed', '#814968', '#eb7b7f', '#2c8397', '#475577', '#d6145f', '#30c381', '#9365b8']

        this.state.topProject = {
            data: {
                labels: data.map(d => d.project_id[1]),
                datasets: [
                    {
                        label: 'Total Tasks',
                        data: data.map(d => d.project_id_count),
                        hoverOffset: 4,
                        backgroundColor: project_data.map(d => color[d.color]),

                    },

                ]
            }
        }
    }
    // Product of Project
    async getTopProductinProject() {
        const color = ['#dadada', '#f06050', '#f4a460', '#f7cd1f', '#6cc1ed', '#814968', '#eb7b7f', '#2c8397', '#475577', '#d6145f', '#30c381', '#9365b8']
        let domain = []
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const data = await this.orm.readGroup('product.ansv', domain, ['project_id'], ['project_id'], { limit: 5, orderby: "create_date desc" })
        const project_data = await this.orm.searchRead('project.ansv', [], ['color'])
        this.state.topProduct = {
            data: {
                labels: data.map(d => d.project_id[1]),
                datasets: [
                    {
                        label: 'Total Products',
                        data: data.map(d => d.project_id_count),
                        hoverOffset: 4,
                        backgroundColor: project_data.map(d => color[d.color]),
                    },

                ]
            }
        }
    }

    //Tassk by Status
    async getTaskbyStatus() {
        let domain = []
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const data = await this.orm.searchRead('project.ansv', domain, ['project_name', 'completed_tasks', 'Incompleted_tasks'])
        // console.log(data)
        this.state.taskByStatus = {
            data: {
                labels: data.map(d => d.project_name),
                datasets: [
                    {
                        label: 'Completed Tasks',
                        data: data.map(d => d.completed_tasks),
                        hoverOffset: 4,
                        // backgroundColor: project_data.map(d => color[d.color]),
                    },
                    {
                        label: 'Incompleted Tasks',
                        data: data.map(d => d.Incompleted_tasks),
                        hoverOffset: 4,
                        // backgroundColor: project_data.map(d => color[d.color]),
                    },
                ]
            }
        }
    }
    //Priority Tasks bar
    async getTaskbyPriority() {
        let domain = []
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const data = await this.orm.searchRead('project.ansv', domain, ['project_name', 'medium_tasks', 'high_tasks', 'urgent_tasks'])
        // console.log(data)
        this.state.taskPriority = {
            data: {
                labels: data.map(d => d.project_name),
                datasets: [
                    {
                        label: 'Medium',
                        data: data.map(d => d.medium_tasks),
                        hoverOffset: 4,
                        backgroundColor: "#a9f451",
                    },
                    {
                        label: 'High',
                        data: data.map(d => d.high_tasks),
                        hoverOffset: 4,
                        backgroundColor: "#fcd382",
                    },
                    {
                        label: 'Urgent',
                        data: data.map(d => d.urgent_tasks),
                        hoverOffset: 4,
                        backgroundColor: "#f56c6c",
                    },
                ]
            }
        }
    }

    // async getTaskbyPriority() {
    //     let domain = []
    //     if (this.state.period > 0) {
    //         domain.push(['create_date', '>', this.state.date])
    //     }
    //     const data = await this.orm.searchRead('project.ansv', domain, ['project_name', 'medium_tasks', 'high_tasks', 'urgent_tasks'])
    //     // console.log(data)
    //     this.state.taskPriority = {
    //         data: {
    //             labels: data.map(d => d.project_name),
    //             datasets: [
    //                 {
    //                     label: 'Medium',
    //                     data: data.map(d => d.medium_tasks),
    //                     hoverOffset: 4,
    //                     backgroundColor: "#a9f451",
    //                 },
    //                 {
    //                     label: 'High',
    //                     data: data.map(d => d.high_tasks),
    //                     hoverOffset: 4,
    //                     backgroundColor: "#fcd382",
    //                 },
    //                 {
    //                     label: 'Urgent',
    //                     data: data.map(d => d.urgent_tasks),
    //                     hoverOffset: 4,
    //                     backgroundColor: "#f56c6c",
    //                 },
    //             ]
    //         }
    //     }
    // }

    //SET UP
    setup() {
        this.state = useState({
            uid: null,
            task: { value: 0, percentage: 0, },
            taskList: [],
            incompletedtask: { value: 0, percentage: 0, },
            completedtask: { value: 0, percentage: 0, },
            mytask: { value: 0, percentage: 0, },
            period: 90,
        })
        this.model = "task.project.ansv"
        this.orm = useService("orm")
        this.actionService = useService("action")

        const old_chartjs = document.querySelector('script[src="/web/static/lib/Chart/Chart.js"]')
        const router = useService("router")

        if (old_chartjs) {
            let { search, hash } = router.current
            search.old_chartjs = old_chartjs != null ? "0" : "1"
            hash.action = 1209
            browser.location.href = browser.location.origin + routeToUrl(router.current)
        }

        onWillStart(async () => {
            this.getDates()
            await this.GetAllTask()
            // console.log(this.state.taskList)
            await this.GetIncompletedTask()
            await this.GetCompletedTask()
            await this.GetMyTask()
            //chart
            await this.getTopProject()
            await this.getTopProductinProject()
            await this.getTaskbyStatus()
            await this.getTaskbyPriority()
        })

    }
    //All tasks
    async GetAllTask() {
        let domain = []
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const countTasks = await this.orm.searchCount(this.model, domain)
        this.state.task.value = countTasks
    }
    viewTasks() {
        let domain = []
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "All Tasks",
            res_model: this.model,
            domain, //same name as domain so dont need to change add value
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ]
        })
    }


    //incomlpeted tasks
    async GetIncompletedTask() {
        //domain default can push though :))
        let domain = [['stage_id', 'in', ['In Progress', 'New', 'Testing']]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const incompletedTasks = await this.orm.searchCount(this.model, domain)
        this.state.incompletedtask.value = incompletedTasks
    }


    viewIncompletedTasks() {
        let domain = [['stage_id', 'in', ['In Progress', 'New', 'Testing']]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Incompleted Tasks",
            res_model: this.model,
            domain, //same name as domain so dont need to change add value
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ]
        })
    }

    //Completed Tasks
    async GetCompletedTask() {
        //domain default can push though :))
        let domain = [['stage_id', 'in', ['Solved', 'Cancelled']]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const completedTasks = await this.orm.searchCount(this.model, domain)
        this.state.completedtask.value = completedTasks
    }

    viewCompletedTasks() {
        let domain = [['stage_id', 'in', ['Solved', 'Cancelled']]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Completed Tasks",
            res_model: this.model,
            domain, //same name as domain so dont need to change add value
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ]
        })
    }
    //Personal Tasks
    async GetMyTask() {
        //domain default can push though :))
        const uid = session.uid
        this.state.uid = uid;
        let domain = [['assignees_id', 'in', this.state.uid]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const myTasks = await this.orm.searchCount(this.model, domain)
        this.state.mytask.value = myTasks
    }

    viewMyTasks() {
        let domain = [['assignees_id', 'in', this.state.uid]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "My Tasks",
            res_model: this.model,
            domain, //same name as domain so dont need to change add value
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ]
        })
    }

    getDates() {
        this.state.date = moment().subtract(this.state.period, 'days').format('L');
    }

    async onChangePeriod() {
        //sử dụng mement của js
        this.getDates()
        await this.GetAllTask()
        await this.GetIncompletedTask()
        await this.GetCompletedTask()
        await this.GetMyTask()

        await this.getTopProject()
        await this.getTopProductinProject()
        await this.getTaskbyStatus()
        await this.getTaskbyPriority()
    }
}

OwlProjectDashboard.template = "owl.ProjectDashboard"
OwlProjectDashboard.components = { KpiCard, ChartRenderer }
registry.category("actions").add("owl.project_dashboard", OwlProjectDashboard)




