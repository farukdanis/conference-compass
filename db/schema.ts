import {sqliteTable,text,integer,primaryKey} from 'drizzle-orm/sqlite-core';
export const dailyCounts=sqliteTable('daily_counts',{
 day:text('day').notNull(),metric:text('metric').notNull(),value:text('value').notNull(),count:integer('count').notNull().default(0)
},t=>[primaryKey({columns:[t.day,t.metric,t.value]})]);
