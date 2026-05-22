import type { Question } from '../types'
import questionsData from '@data/output/questions.json'

export const questions = questionsData as Record<string, Question[]>
