/** @odoo-module */

import { registry } from "@web/core/registry"
import { kanbanView } from "@web/views/kanban/kanban_view"
import { KanbanController } from "@web/views/kanban/kanban_controller"
import { useService } from '@web/core/utils/hooks';
const { Component, onWillStart, useRef, onMounted, useState } = owl
//lấy color không bị trùng
import { getColor } from "@web/views/graph/colors"
//this will select the current web right now
var session = require('web.session');
//reload page
class HelpdeskKanBanController extends KanbanController {
    setup() {
        super.setup()
        this.action = useService("action")
        this.orm = useService("orm")
        this.MyOpenTicket = 0
        this.MajorTicket = 0
        this.CriticalTicket = 0
        this.FailedTicket = 0

        onWillStart(async () => {
            await this.GetMyOpenTicket()
            await this.GetMyMajorTicket()
            await this.GetMyCriticalTicket()
            await this.GetFailedTicket()
            await this.GetAvgOpenHour()
            await this.GetAvgOpenHourMajor()
            await this.GetAvgOpenHourCritical()
        })
    }
    //GET CURRENT USER TICKET
    async GetMyOpenTicket() {
        const uid = session.uid
        let domain = [['assign_to', '=', uid], ['is_closed', '=', false]]
        const countMyTicket = await this.orm.searchCount("helpdesk.ticket", domain)
        this.MyOpenTicket = countMyTicket
        // console.log(countMyTicket)
    }

    async GetMyMajorTicket() {
        const uid = session.uid
        let domain = [['assign_to', '=', uid], ['is_closed', '=', false], ['priority', '=', 2]]
        const MyMajorTicket = await this.orm.searchCount("helpdesk.ticket", domain)
        this.MajorTicket = MyMajorTicket
    }

    async GetMyCriticalTicket() {
        const uid = session.uid
        let domain = [['assign_to', '=', uid], ['is_closed', '=', false], ['priority', '=', 3]]
        const MyCriticalTicket = await this.orm.searchCount("helpdesk.ticket", domain)
        this.CriticalTicket = MyCriticalTicket
    }
    //GEt FAILED TICKET
    async GetFailedTicket() {
        const uid = session.uid
        let domain = [['assign_to', '=', uid], ['is_failed', '=', true]]
        let domain_major = [['assign_to', '=', uid], ['is_failed', '=', true], ['priority', '=', 2]]
        let domain_critical = [['assign_to', '=', uid], ['is_failed', '=', true], ['priority', '=', 3]]
        const failedTicket = await this.orm.searchCount("helpdesk.ticket", domain)
        const MyMajorFailedTicket = await this.orm.searchCount("helpdesk.ticket", domain_major)
        const MyCriticalFailedTicket = await this.orm.searchCount("helpdesk.ticket", domain_critical)
        this.FailedTicket = failedTicket
        this.MajorFailedTicket = MyMajorFailedTicket
        this.CriticalFailedTicket = MyCriticalFailedTicket
    }

    //Open Hour
    async GetAvgOpenHour() {
        const uid = session.uid
        let domain = [['assign_to', '=', uid], ['is_closed', '=', false]]
        let ticketListDate = []
        let jsdate = []
        let open_hour = []
        var current_date = new Date();
        ticketListDate = await this.orm.searchRead("helpdesk.ticket", domain, ["name", "create_date_js"])
        if (ticketListDate.length != 0) {
            for (let i = 0; i < ticketListDate.length; i++) {
                jsdate.push(new Date(ticketListDate[i].create_date_js));
            }
            for (let i = 0; i < jsdate.length; i++) {
                open_hour.push((current_date - jsdate[i]) / (1000 * 60 * 60))
            }
            // Using the reduce() method to calculate the sum of the numbers
            var sum = open_hour.reduce((accumulator, currentValue) => {
                return accumulator + currentValue;
            }, 0);

            // Calculate the average by dividing the sum by the number of elements in the array
            let average = sum / open_hour.length;
            this.AverageOpenHour = average.toFixed(0)
        }
        else {
            this.AverageOpenHour = 0
        }

        console.log(this.AverageOpenHour);
    }

    async GetAvgOpenHourMajor() {
        const uid = session.uid
        let domain = [['assign_to', '=', uid], ['is_closed', '=', false], ['priority', '=', 2]]
        let ticketListDate = []
        let jsdate = []
        let open_hour = []
        var current_date = new Date();
        ticketListDate = await this.orm.searchRead("helpdesk.ticket", domain, ["name", "create_date_js"])
        if (ticketListDate.length != 0) {
            for (let i = 0; i < ticketListDate.length; i++) {
                jsdate.push(new Date(ticketListDate[i].create_date_js));
            }
            for (let i = 0; i < jsdate.length; i++) {
                open_hour.push((current_date - jsdate[i]) / (1000 * 60 * 60))
            }
            // Using the reduce() method to calculate the sum of the numbers
            var sum = open_hour.reduce((accumulator, currentValue) => {
                return accumulator + currentValue;
            }, 0);

            // Calculate the average by dividing the sum by the number of elements in the array
            let average = sum / open_hour.length;
            this.AverageOpenHourMajor = average.toFixed(0)
        }
        else {
            this.AverageOpenHourMajor = 0
        }
    }

    async GetAvgOpenHourCritical() {
        const uid = session.uid
        let domain = [['assign_to', '=', uid], ['is_closed', '=', false], ['priority', '=', 3]]
        let ticketListDate = []
        let jsdate = []
        let open_hour = []
        var current_date = new Date();
        ticketListDate = await this.orm.searchRead("helpdesk.ticket", domain, ["name", "create_date_js"])
        if (ticketListDate.length != 0) {
            for (let i = 0; i < ticketListDate.length; i++) {
                jsdate.push(new Date(ticketListDate[i].create_date_js));
            }
            for (let i = 0; i < jsdate.length; i++) {
                open_hour.push((current_date - jsdate[i]) / (1000 * 60 * 60))
            }
            // Using the reduce() method to calculate the sum of the numbers
            var sum = open_hour.reduce((accumulator, currentValue) => {
                return accumulator + currentValue;
            }, 0);

            // Calculate the average by dividing the sum by the number of elements in the array
            let average = sum / open_hour.length;
            this.AverageOpenHourCritical = average.toFixed(0)
        }
        else {
            this.AverageOpenHourCritical = 0
        }
    }

    enableEditing() {
        console.log("CLickk...");
    }
}

export const helpDeskKanbanView = {
    //Lấy tất cả attrs của listView
    ...kanbanView,
    //Thay thế controller bằng controller trên
    Controller: HelpdeskKanBanController,
}

HelpdeskKanBanController.template = "owl.HelpdeskTableKanbanView"

registry.category("views").add("helpdesk_table_kanban_view", helpDeskKanbanView);